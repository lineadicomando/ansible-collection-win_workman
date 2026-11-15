# Upgrade OpenSSH Server from a Win32-OpenSSH MSI. Run by openssh-update as SYSTEM from
# a scheduled task, outside the SSH session it was started from: msiexec stops sshd
# and replaces the binaries that session runs on. The play reconnects and waits for
# the outcome in $Dir\result.json, written last.
#
# The MSI is a major upgrade of the installed one (same UpgradeCode): if it fails,
# Windows Installer rolls back to the previous version by itself. What this script
# adds is putting back what an upgrade may drop (the HKLM\SOFTWARE\OpenSSH values such
# as DefaultShell, sshd_config) and making sure sshd runs again, whatever happened.
param(
    [Parameter(Mandatory)] [string]$Msi,
    [Parameter(Mandatory)] [string]$Dir
)
$ErrorActionPreference = 'Stop'
$result = [ordered]@{
    started = (Get-Date).ToString('o')
    msi_exit = $null
    restored = @()
    service_state = $null
    version = $null
    errors = @()
}
function Write-Result {
    $result.finished = (Get-Date).ToString('o')
    # UTF-8 without BOM: Set-Content -Encoding UTF8 of PowerShell 5.1 writes one, and
    # from_json on the controller rejects it.
    [IO.File]::WriteAllText("$Dir\result.json", ($result | ConvertTo-Json -Depth 4))
}
function Get-OpenSshVersion {
    $keys = 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*'
    $p = Get-ItemProperty -Path $keys -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -eq 'OpenSSH' -and $_.PSChildName -match '^\{' } |
        Select-Object -First 1
    if ($p) { $p.DisplayVersion } else { $null }
}

New-Item -ItemType File -Force -Path "$Dir\started" | Out-Null
$regPath = 'HKLM:\SOFTWARE\OpenSSH'
$regSaved = @{}
try {
    if (Test-Path $regPath) {
        $item = Get-Item -Path $regPath
        foreach ($name in $item.GetValueNames()) {
            $regSaved[$name] = @{ value = $item.GetValue($name); kind = $item.GetValueKind($name) }
        }
    }
    $cfgDir = Join-Path $env:ProgramData 'ssh'
    $backup = Join-Path $Dir 'programdata-ssh'
    if (Test-Path $cfgDir) {
        New-Item -ItemType Directory -Force -Path $backup | Out-Null
        Get-ChildItem -LiteralPath $cfgDir -File | Copy-Item -Destination $backup -Force
    }

    Stop-Service -Name sshd -Force -ErrorAction SilentlyContinue
    $p = Start-Process msiexec.exe -Wait -PassThru `
        -ArgumentList "/i `"$Msi`" /qn /norestart /l*v `"$Dir\msiexec.log`""
    $result.msi_exit = $p.ExitCode
    if ($p.ExitCode -notin 0, 3010) {
        $result.errors += "msiexec exited with $($p.ExitCode); Windows Installer rolled back to the previous version"
    }
} catch {
    $result.errors += "upgrade: $($_.Exception.Message)"
}

# Whatever happened above, put back what is missing and get sshd running again.
try {
    if (-not (Test-Path $regPath)) { New-Item -Path $regPath -Force | Out-Null }
    $item = Get-Item -Path $regPath
    foreach ($name in $regSaved.Keys) {
        if ($item.GetValueNames() -notcontains $name) {
            New-ItemProperty -Path $regPath -Name $name -Value $regSaved[$name].value `
                -PropertyType $regSaved[$name].kind -Force | Out-Null
            $result.restored += "registry $name"
        }
    }
    if (Test-Path $backup) {
        foreach ($f in Get-ChildItem -LiteralPath $backup -File) {
            $dest = Join-Path $cfgDir $f.Name
            if (-not (Test-Path -LiteralPath $dest)) {
                Copy-Item -LiteralPath $f.FullName -Destination $dest
                $result.restored += $f.Name
            }
        }
    }
} catch {
    $result.errors += "restore: $($_.Exception.Message)"
}
for ($i = 1; $i -le 5; $i++) {
    try {
        Set-Service -Name sshd -StartupType Automatic
        Start-Service -Name sshd
        break
    } catch {
        if ($i -eq 5) { $result.errors += "start sshd: $($_.Exception.Message)" }
        Start-Sleep -Seconds 3
    }
}
$svc = Get-Service -Name sshd -ErrorAction SilentlyContinue
$result.service_state = if ($svc) { $svc.Status.ToString() } else { 'missing' }
$result.version = Get-OpenSshVersion
Write-Result

# win_workman per-user deferred install agent.
#
# Deployed by the usr action of pkg_utils. A scheduled task with principal
# BUILTIN\Users starts it at every logon, in the context of the user logging on,
# and usr-apply starts the same task on demand for the users already logged on.
# It applies every policy under policies\ to the current user: installs,
# upgrades or uninstalls a per-user package, and records the outcome under
# HKCU\Software\win_workman\usr\<schema>, where usr-info reads it back.
#
# Must run in Windows PowerShell 5.1 without elevation. Keep it self-contained:
# users can read this directory but not write to it, which is what makes it safe
# to run as every user who logs on.
param([string]$Root = $PSScriptRoot)

$ErrorActionPreference = 'Stop'

$logDir = Join-Path $env:LOCALAPPDATA 'win_workman'
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir 'usr-agent.log'
$receiptRoot = 'HKCU:\Software\win_workman\usr'

function Write-Log {
  param([string]$Message)
  "$(Get-Date -Format o) $Message" | Add-Content -LiteralPath $logFile -Encoding UTF8
}

function Get-UtcStamp {
  (Get-Date).ToUniversalTime().ToString('o')
}

function Set-Receipt {
  param([string]$Schema, [hashtable]$Values)
  $key = Join-Path $receiptRoot $Schema
  if (-not (Test-Path -LiteralPath $key)) { New-Item -Path $key -Force | Out-Null }
  foreach ($name in $Values.Keys) {
    Set-ItemProperty -LiteralPath $key -Name $name -Value ([string]$Values[$name])
  }
}

function Get-DesiredState {
  # The most specific rule wins: an entry naming the user beats any group entry.
  # Among group entries that disagree, absent wins, so excluding a group is safe.
  param($Policy, [string]$UserSid, [hashtable]$GroupSids)
  $targets = @($Policy.targets)
  $userEntry = @($targets | Where-Object { $_.sid -eq $UserSid })
  if ($userEntry.Count -gt 0) { return [string]$userEntry[0].state }
  $groupStates = @($targets | Where-Object { $GroupSids.ContainsKey([string]$_.sid) } | ForEach-Object { [string]$_.state })
  if ($groupStates -contains 'absent') { return 'absent' }
  if ($groupStates -contains 'present') { return 'present' }
  return $null
}

function Get-UninstallEntry {
  param([string]$Key)
  Get-ItemProperty -LiteralPath "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\$Key" -ErrorAction SilentlyContinue
}

function Compare-PkgVersion {
  param([string]$Left, [string]$Right)
  $l = $null; $r = $null
  if ([version]::TryParse($Left, [ref]$l) -and [version]::TryParse($Right, [ref]$r)) {
    return $l.CompareTo($r)
  }
  return [string]::Compare($Left, $Right, $true)
}

function Invoke-Setup {
  param([string]$Path, [object[]]$Arguments, [int]$TimeoutSec)
  $argLine = (@($Arguments) | ForEach-Object {
    $a = [string]$_
    if ($a -match '\s' -and $a -notmatch '^".*"$') { '"' + $a + '"' } else { $a }
  }) -join ' '
  $startArgs = @{ FilePath = $Path; PassThru = $true; WindowStyle = 'Hidden' }
  if ($argLine) { $startArgs['ArgumentList'] = $argLine }
  $proc = Start-Process @startArgs
  # Touching Handle keeps it open, otherwise ExitCode can come back empty.
  $null = $proc.Handle
  if (-not $proc.WaitForExit($TimeoutSec * 1000)) {
    try { $proc.Kill() } catch { }
    throw "'$Path' still running after ${TimeoutSec}s"
  }
  return [int]$proc.ExitCode
}

function Split-CommandPath {
  param([string]$CommandLine)
  $c = $CommandLine.Trim()
  if ($c.StartsWith('"')) { return $c.Substring(1, $c.IndexOf('"', 1) - 1) }
  $exe = $c.IndexOf('.exe', [StringComparison]::OrdinalIgnoreCase)
  if ($exe -ge 0) { return $c.Substring(0, $exe + 4) }
  return $c
}

# One run per session at a time: the logon trigger and usr-apply can overlap.
$mutex = New-Object System.Threading.Mutex($false, 'Local\win_workman_usr_agent')
if (-not $mutex.WaitOne(0)) {
  Write-Log 'another agent run is in progress in this session, exiting'
  exit 0
}

$exitCode = 0
try {
  $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
  $userSid = $identity.User.Value
  $groupSids = @{}
  foreach ($group in $identity.Groups) { $groupSids[$group.Value] = $true }

  $policyFiles = @(Get-ChildItem -LiteralPath (Join-Path $Root 'policies') -Filter '*.json' -ErrorAction SilentlyContinue | Sort-Object Name)
  Write-Log "start user=$($identity.Name) policies=$($policyFiles.Count)"

  foreach ($file in $policyFiles) {
    $schema = $file.BaseName
    try {
      $policy = Get-Content -LiteralPath $file.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
      $desired = Get-DesiredState -Policy $policy -UserSid $userSid -GroupSids $groupSids
      if (-not $desired) { continue }

      $timeout = if ($policy.timeout) { [int]$policy.timeout } else { 900 }
      $successCodes = @($policy.success_exit_codes | ForEach-Object { [int]$_ })
      if ($successCodes.Count -eq 0) { $successCodes = @(0) }
      $entry = Get-UninstallEntry -Key $policy.uninstall_key
      $installed = if ($entry) { [string]$entry.DisplayVersion } else { '' }

      if ($desired -eq 'present') {
        # Never downgrade: packages such as Zed update themselves in the profile.
        if ($installed -and (Compare-PkgVersion $installed ([string]$policy.version)) -ge 0) {
          Set-Receipt $schema @{ State = 'present'; Result = 'ok'; Changed = 'False'; Version = $installed; Message = 'already installed'; Timestamp = (Get-UtcStamp) }
          continue
        }
        $setup = Join-Path ([string]$policy.payload_dir) ([string]$policy.setup_file)
        if (-not (Test-Path -LiteralPath $setup -PathType Leaf)) { throw "payload not found: $setup" }
        if ($policy.sha256) {
          $hash = (Get-FileHash -LiteralPath $setup -Algorithm SHA256).Hash
          if ($hash -ne ([string]$policy.sha256).ToUpperInvariant()) { throw "checksum mismatch for $setup" }
        }
        Write-Log "${schema}: installing $($policy.version) (installed: '$installed')"
        $code = Invoke-Setup -Path $setup -Arguments @($policy.install_args) -TimeoutSec $timeout
        if ($successCodes -notcontains $code) { throw "installer exited with code $code" }
        $entry = Get-UninstallEntry -Key $policy.uninstall_key
        if (-not $entry) { throw "installer exited with code $code but uninstall key '$($policy.uninstall_key)' is missing" }
        Set-Receipt $schema @{ State = 'present'; Result = 'ok'; Changed = 'True'; Version = [string]$entry.DisplayVersion; Message = "installed (exit $code)"; Timestamp = (Get-UtcStamp) }
        Write-Log "${schema}: installed $($entry.DisplayVersion)"
      }
      else {
        if (-not $entry) {
          Set-Receipt $schema @{ State = 'absent'; Result = 'ok'; Changed = 'False'; Version = ''; Message = 'not installed'; Timestamp = (Get-UtcStamp) }
          continue
        }
        $uninstaller = Split-CommandPath ([string]$entry.UninstallString)
        if (-not (Test-Path -LiteralPath $uninstaller -PathType Leaf)) { throw "uninstaller not found: $uninstaller" }
        Write-Log "${schema}: uninstalling $installed"
        $code = Invoke-Setup -Path $uninstaller -Arguments @($policy.uninstall_args) -TimeoutSec $timeout
        if ($successCodes -notcontains $code) { throw "uninstaller exited with code $code" }
        # Inno Setup and NSIS uninstallers relaunch themselves from %TEMP% and
        # return at once: the uninstall key going away is the real completion.
        $deadline = (Get-Date).AddSeconds($timeout)
        while ((Get-UninstallEntry -Key $policy.uninstall_key) -and (Get-Date) -lt $deadline) { Start-Sleep -Seconds 2 }
        if (Get-UninstallEntry -Key $policy.uninstall_key) { throw "uninstall key still present after ${timeout}s" }
        Set-Receipt $schema @{ State = 'absent'; Result = 'ok'; Changed = 'True'; Version = ''; Message = "uninstalled (exit $code)"; Timestamp = (Get-UtcStamp) }
        Write-Log "${schema}: uninstalled"
      }
    }
    catch {
      $exitCode = 1
      Write-Log "${schema}: ERROR $($_.Exception.Message)"
      Set-Receipt $schema @{ Result = 'error'; Changed = 'False'; Message = $_.Exception.Message; Timestamp = (Get-UtcStamp) }
    }
  }
}
finally {
  if (-not (Test-Path -LiteralPath $receiptRoot)) { New-Item -Path $receiptRoot -Force | Out-Null }
  Set-ItemProperty -LiteralPath $receiptRoot -Name 'LastRun' -Value (Get-UtcStamp)
  Write-Log "end exit=$exitCode"
  $mutex.ReleaseMutex()
}
exit $exitCode

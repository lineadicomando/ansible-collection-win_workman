#!/usr/bin/env bash
# Releases a new version of the collection: bumps galaxy.yml, commits, tags
# and pushes branch and tag together. With --pin, it then points the
# requirements file of a project that uses the collection at the new tag, and
# commits and pushes that too.
#
#   tools/release.sh patch|minor|major [--pin FILE]... [--trailer LINE] [--dry-run]
#
#   patch   package version updates and small fixes            0.7.0 -> 0.7.1
#   minor   new roles or actions, changes of default behaviour  0.7.1 -> 0.8.0
#   major   breaking changes, once the collection reaches 1.0   0.8.0 -> 1.0.0
#
#   --pin FILE      a requirements file whose win_workman entry gets the new
#                   tag; it must live in a git work tree. Repeatable
#   --trailer LINE  appended to every commit message after a blank line,
#                   e.g. a Co-Authored-By line
#   --dry-run       print what would change, touch nothing
#
# Branch and tag go out in one atomic push: a push mirror that syncs on every
# push runs once, instead of two runs racing each other, where the losing one
# is rejected and drops the tag.
set -euo pipefail

usage() { sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'; exit "${1:-2}"; }

level="" ; pins=() ; trailer="" ; dry=false
while [ $# -gt 0 ]; do
  case "$1" in
    patch|minor|major) level="$1" ;;
    --pin) pins+=("$(realpath "${2:?--pin needs a file}")"); shift ;;
    --trailer) trailer="${2:?--trailer needs a line}"; shift ;;
    --dry-run) dry=true ;;
    -h|--help) usage 0 ;;
    *) echo "unknown argument: $1" >&2; usage ;;
  esac
  shift
done
[ -n "$level" ] || usage

die() { echo "release: $*" >&2; exit 1; }
message() { if [ -n "$trailer" ]; then printf '%s\n\n%s\n' "$1" "$trailer"; else printf '%s\n' "$1"; fi; }

repo="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$repo"

# The collection: clean, on main, level with origin
[ "$(git branch --show-current)" = main ] || die "not on main"
[ -z "$(git status --porcelain)" ] || die "uncommitted changes in $repo"
git fetch -q origin
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] || die "main is not level with origin/main"

current="$(sed -n 's/^version: *\([0-9]*\.[0-9]*\.[0-9]*\) *$/\1/p' galaxy.yml)"
[ -n "$current" ] || die "no version in galaxy.yml"
IFS=. read -r major minor patch <<<"$current"
case "$level" in
  patch) patch=$((patch + 1)) ;;
  minor) minor=$((minor + 1)); patch=0 ;;
  major) major=$((major + 1)); minor=0; patch=0 ;;
esac
next="$major.$minor.$patch"
tag="v$next"
git rev-parse -q --verify "refs/tags/$tag" >/dev/null && die "tag $tag already exists"

# The pins: each one in a clean work tree, with a win_workman entry
for pin in "${pins[@]}"; do
  [ -f "$pin" ] || die "$pin: no such file"
  pin_repo="$(git -C "$(dirname "$pin")" rev-parse --show-toplevel)" || die "$pin is not in a git work tree"
  [ -z "$(git -C "$pin_repo" status --porcelain)" ] || die "uncommitted changes in $pin_repo"
  grep -q 'ansible-collection-win_workman' "$pin" || die "$pin has no win_workman entry"
done

echo "win_workman $current -> $next ($tag)"
if $dry; then
  echo "would commit galaxy.yml, tag $tag, push main and $tag to origin"
  for pin in "${pins[@]}"; do echo "would pin $pin to $tag"; done
  exit 0
fi

sed -i "s/^version: *$current *\$/version: $next/" galaxy.yml
git commit -q -m "$(message "Bump the version to $next")" galaxy.yml
git tag -a "$tag" -m "$tag"
git push -q --atomic origin main "$tag"
echo "pushed main and $tag"

for pin in "${pins[@]}"; do
  pin_repo="$(git -C "$(dirname "$pin")" rev-parse --show-toplevel)"
  # The version line of the win_workman entry, whatever it says now
  sed -i "/ansible-collection-win_workman/,/version:/ s/version: .*/version: $tag/" "$pin"
  if git -C "$pin_repo" diff --quiet -- "$pin"; then
    echo "$pin already on $tag"
    continue
  fi
  git -C "$pin_repo" commit -q -m "$(message "Pin win_workman to $tag")" -- "$pin"
  git -C "$pin_repo" push -q origin HEAD
  echo "pinned $pin to $tag and pushed"
done

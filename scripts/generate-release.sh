#!/usr/bin/env bash
#
# generate-release.sh — materialize the packaging files for a new OCS
# Inventory release, from a single version string (normally a git tag).
#
# For each component (ocsinventory-backend, ocsinventory-frontend,
# ocsinventory-agent, ocsinventory-server):
#   - deb/<pkg>/debian/changelog gets a new entry (via `dch`)
#   - rpm/specs/<pkg>.spec gets %define version/release bumped and a new
#     %changelog entry
# For docker-enabled components (backend, frontend, server):
#   - docker/<version>/ is created by copying the most recent existing
#     release directory (excluding "dev") and stamping the new version
#     into every file that referenced the old one.
#
# NOTE: ocsinventory-release is intentionally NOT touched here. It bundles
# the YUM repo config + GPG key and is versioned independently of app
# releases (see REDHAT.md).
#
# Usage:
#   ./scripts/generate-release.sh <version>
#
#   <version> looks like 3.1.0 or 3.1.0-rc1 (same style as the git tag,
#   hyphen for the pre-release separator). It gets converted to the
#   tilde-separated form (3.1.0~rc1) for deb/rpm, since dpkg/rpm reserve
#   "-" for the upstream/revision separator.
#
# Env overrides:
#   DEBIAN_RELEASE   deb package revision, default "1"
#   RPM_RELEASE      rpm package release, default "1"
#   DEBFULLNAME/DEBEMAIL   used by dch for the changelog trailer
#
set -euo pipefail

VERSION="${1:-}"
if [[ -z "$VERSION" ]]; then
  echo "usage: $0 <version>   (e.g. 3.1.0 or 3.1.0-rc1)" >&2
  exit 1
fi

if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9]+)?$ ]]; then
  echo "error: '$VERSION' doesn't look like X.Y.Z or X.Y.Z-suffix" >&2
  exit 1
fi

DEBIAN_RELEASE="${DEBIAN_RELEASE:-1}"
RPM_RELEASE="${RPM_RELEASE:-1}"
: "${DEBFULLNAME:=OCS Inventory Release Bot}"
: "${DEBEMAIL:=ci@ocsinventory-ng.org}"
export DEBFULLNAME DEBEMAIL
# changelog dates (dch's trailer, our own %changelog entry) must stay in
# the conventional English format regardless of the runner's locale
export LC_TIME=C

# rpm/deb use "~" (sorts before nothing) instead of "-" for pre-releases
PKG_VERSION="${VERSION/-/\~}"

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

COMPONENTS=(ocsinventory-backend ocsinventory-frontend ocsinventory-agent ocsinventory-server)
DOCKER_COMPONENTS=(ocsinventory-backend ocsinventory-frontend ocsinventory-server)

changed_files=()

sed_escape() {
  printf '%s' "$1" | sed 's/[.[\*^$/]/\\&/g'
}

echo "== generating release $VERSION (package version: $PKG_VERSION) =="

# ---------------------------------------------------------------------------
# 1. docker/<version>/ — clone the latest existing release dir, stamp version
# ---------------------------------------------------------------------------
for pkg in "${DOCKER_COMPONENTS[@]}"; do
  docker_dir="$pkg/docker"
  [[ -d "$docker_dir" ]] || continue

  target="$docker_dir/$VERSION"
  if [[ -d "$target" ]]; then
    echo "-- $target already exists, skipping docker scaffolding for $pkg"
    continue
  fi

  latest_dir=""
  latest_ver=""
  for d in "$docker_dir"/*/; do
    d="${d%/}"
    base="$(basename "$d")"
    [[ "$base" == "dev" ]] && continue
    if [[ -z "$latest_ver" ]] || dpkg --compare-versions "${base/-/\~}" gt "${latest_ver/-/\~}"; then
      latest_ver="$base"
      latest_dir="$d"
    fi
  done

  if [[ -z "$latest_dir" ]]; then
    echo "error: no existing release dir under $docker_dir to use as a template" >&2
    exit 1
  fi

  echo "-- $pkg: generating docker/$VERSION from docker/$latest_ver"
  cp -r "$latest_dir" "$target"

  pattern="$(sed_escape "$latest_ver")"
  while IFS= read -r -d '' f; do
    sed -i "s/$pattern/$VERSION/g" "$f"
  done < <(grep -rlFZ "$latest_ver" "$target")

  changed_files+=("$target")
done

# ---------------------------------------------------------------------------
# 2. debian/changelog — new entry via dch (non-interactive: message as arg)
# ---------------------------------------------------------------------------
for pkg in "${COMPONENTS[@]}"; do
  changelog="$pkg/deb/$pkg/debian/changelog"
  [[ -f "$changelog" ]] || continue

  # keep whatever epoch the package already uses (e.g. "3:")
  epoch=""
  if [[ "$(head -1 "$changelog")" =~ \(([0-9]+): ]]; then
    epoch="${BASH_REMATCH[1]}:"
  fi
  full_version="${epoch}${PKG_VERSION}-${DEBIAN_RELEASE}"

  echo "-- $pkg: dch -v $full_version"
  dch --changelog "$changelog" --newversion "$full_version" --distribution stable \
      "Release $VERSION."

  changed_files+=("$changelog")
done

# ---------------------------------------------------------------------------
# 3. rpm spec — bump %define version/release + append %changelog entry
# ---------------------------------------------------------------------------
today="$(date -u '+%a %b %d %Y')"
for pkg in "${COMPONENTS[@]}"; do
  spec="$pkg/rpm/specs/$pkg.spec"
  [[ -f "$spec" ]] || continue

  echo "-- $pkg: bumping spec to $PKG_VERSION-$RPM_RELEASE"
  sed -i "s/^%define version .*/%define version ${PKG_VERSION}/" "$spec"
  sed -i "s/^%define release .*/%define release ${RPM_RELEASE}/" "$spec"

  if grep -q '^%changelog' "$spec"; then
    entry="* ${today} ${DEBFULLNAME} <${DEBEMAIL}> - ${PKG_VERSION}-${RPM_RELEASE}\n- Release ${VERSION}.\n"
    awk -v entry="$entry" '
      /^%changelog/ { print; print entry; next }
      { print }
    ' "$spec" > "$spec.tmp"
    mv "$spec.tmp" "$spec"
  fi

  changed_files+=("$spec")
done

echo
echo "== done. changed paths: =="
printf ' - %s\n' "${changed_files[@]}"

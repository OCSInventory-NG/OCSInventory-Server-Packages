#!/usr/bin/env bash
# Lightweight, dependency-free checks for packaging metadata consistency
# across RPM specs and Debian control files. Meant to catch the kind of
# drift that accumulates when several people edit packages independently:
# inconsistent Maintainer domains, non-executable debian/rules, stray
# whitespace, CRLF line endings.
#
# This script never exits non-zero on its own; findings are printed and
# the caller (CI job) decides whether to fail based on FAIL_ON_FINDINGS.
set -u

REPO_ROOT="$(git rev-parse --show-toplevel)"
cd "$REPO_ROOT"

findings=0

warn() {
    printf '::warning::%s\n' "$1"
    findings=$((findings + 1))
}

echo "== debian/rules executable bit =="
while IFS= read -r -d '' rules; do
    if [ ! -x "$rules" ]; then
        warn "$rules is not executable (dpkg-buildpackage will patch it up with a warning at build time; fix with 'chmod +x')"
    fi
done < <(git ls-files -z -- '*/debian/rules')

echo "== Maintainer email domain consistency (control files) =="
domains=$(git ls-files -- '*/debian/control' | xargs -r grep -h '^Maintainer:' | sed -E 's/.*@([^>]+)>.*/\1/' | sort -u)
domain_count=$(printf '%s\n' "$domains" | grep -c .)
if [ "$domain_count" -gt 1 ]; then
    warn "Maintainer email domains are not consistent across debian/control files: $(printf '%s' "$domains" | paste -sd, -)"
    git ls-files -- '*/debian/control' | while IFS= read -r f; do
        grep -H '^Maintainer:' "$f"
    done
fi

echo "== Trailing whitespace =="
while IFS= read -r -d '' f; do
    case "$f" in
        *.gpg|*RPM-GPG-KEY*) continue ;;
    esac
    if grep -qI ' $' "$f" 2>/dev/null; then
        warn "$f has trailing whitespace"
    fi
done < <(git ls-files -z)

echo "== CRLF line endings =="
while IFS= read -r -d '' f; do
    case "$f" in
        *.gpg|*RPM-GPG-KEY*) continue ;;
    esac
    if grep -qI $'\r$' "$f" 2>/dev/null; then
        warn "$f has CRLF line endings"
    fi
done < <(git ls-files -z)

echo "== dpkg-parsechangelog syntax =="
while IFS= read -r -d '' changelog; do
    if ! dpkg-parsechangelog -l "$changelog" >/dev/null 2>/tmp/changelog-err; then
        warn "$changelog failed to parse: $(cat /tmp/changelog-err)"
    fi
done < <(git ls-files -z -- '*/debian/changelog')

echo
echo "Total findings: $findings"

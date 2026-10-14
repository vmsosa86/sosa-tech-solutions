#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="$repo_root/deploy/public-files.txt"
output_dir="$repo_root/.deploy/public"

case "$output_dir" in
  "$repo_root"/.deploy/*) ;;
  *) echo "Refusing unsafe output directory: $output_dir" >&2; exit 1 ;;
esac

# The build scripts need Python 3.8+. Hostinger's default python3 is 3.6, so prefer a newer
# interpreter when one exists (override with PYTHON_BIN=/path/to/python3).
if [[ -z "${PYTHON_BIN:-}" ]]; then
  for candidate in python3.13 python3.12 python3.11 /opt/alt/python311/bin/python3 python3.10 python3.9 python3.8 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>/dev/null; then
      PYTHON_BIN="$candidate"
      break
    fi
  done
fi
if [[ -z "${PYTHON_BIN:-}" ]]; then
  echo "Python 3.8 or newer is required to build the site." >&2
  exit 1
fi

# The Spanish pages, sitemap.xml and llms.txt are generated and committed; refuse to publish
# them stale (an English edit without its regenerated /es/ twin).
"$PYTHON_BIN" "$repo_root/scripts/build_language_pages.py" --check

rm -rf "$output_dir"
mkdir -p "$output_dir"

while IFS= read -r entry || [[ -n "$entry" ]]; do
  [[ -z "$entry" || "$entry" == \#* ]] && continue
  case "$entry" in
    /*|*..*) echo "Unsafe manifest entry: $entry" >&2; exit 1 ;;
  esac
  [[ -e "$repo_root/$entry" ]] || { echo "Missing public path: $entry" >&2; exit 1; }
  (cd "$repo_root" && rsync -aR --exclude='.DS_Store' "./$entry" "$output_dir/")
done < "$manifest"

for forbidden in .git .agents brand deploy scripts tools tmp content/audio content/launch content/assets/kie-sources output README.md BLOG_HANDOFF.md BRAND_CONTENT_GROWTH_PLAN.md; do
  [[ ! -e "$output_dir/$forbidden" ]] || { echo "Internal path entered public output: $forbidden" >&2; exit 1; }
done

# Extra arguments go to the validator, e.g. --allow-missing /services/new-page/ while a
# page is still being built. deploy_hostinger.sh passes none, so deploys stay strict.
"$PYTHON_BIN" "$repo_root/scripts/validate_site.py" --root "$output_dir" "$@"
echo "Public site built at $output_dir"

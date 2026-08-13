#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
manifest="$repo_root/deploy/public-files.txt"
output_dir="$repo_root/.deploy/public"

case "$output_dir" in
  "$repo_root"/.deploy/*) ;;
  *) echo "Refusing unsafe output directory: $output_dir" >&2; exit 1 ;;
esac

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

python3 "$repo_root/scripts/validate_site.py" --root "$output_dir"
echo "Public site built at $output_dir"

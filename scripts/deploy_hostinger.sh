#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
public_dir="/home/u876565679/domains/sosatechsolutions.com/public_html"
backup_root="/home/u876565679/site-backups"
mode="${1:---dry-run}"

case "$mode" in
  --dry-run|--apply) ;;
  *) echo "Usage: $0 [--dry-run|--apply]" >&2; exit 2 ;;
esac

[[ -d "$public_dir" ]] || { echo "Expected document root not found: $public_dir" >&2; exit 1; }
"$repo_root/scripts/build_public_site.sh"

rsync_args=(-a --delete --itemize-changes --exclude=/.well-known/)
if [[ "$mode" == "--dry-run" ]]; then
  rsync_args+=(-n)
  echo "Dry run only. No production files will change."
else
  timestamp="$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$backup_root"
  backup="$backup_root/sosatechsolutions.com-before-$timestamp.tar.gz"
  tar --exclude='./.git' --exclude='./.deploy' -czf "$backup" -C "$public_dir" .
  echo "Backup created: $backup"
fi

rsync "${rsync_args[@]}" "$repo_root/.deploy/public/" "$public_dir/"
echo "Sosa Tech deployment ${mode#--} complete."

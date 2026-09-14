#!/usr/bin/env bash
# Call only after the previous build has stopped. Keeps both ABI sysroots intact.
set -euo pipefail
scratch=/home/arron/projects/openjdk26-android-build
target=${1:?Expected arm or aarch64}
case "$target" in arm|aarch64) ;; *) exit 2;; esac
exec 9>/tmp/.jdk26-staging.lock
flock -n 9 || { echo 'Another JDK26 build owns the staging prefix' >&2; exit 2; }
current=$(cat /data/TERMUX_ARCH)
case "$current" in arm|aarch64) ;; *) echo 'Unrecognized staging owner' >&2; exit 2;; esac
if [[ "$current" == "$target" ]]; then exit 0; fi
mkdir -p "$scratch/staging"
backup="$scratch/staging/$current-data"
restore="$scratch/staging/$target-data"
[[ ! -e "$backup" ]] || { echo "Refusing to overwrite saved staging: $backup" >&2; exit 2; }
# Both paths are literal descendants of this task's scratch root.
[[ $(realpath -m "$backup") == "$scratch/staging/$current-data" ]] || exit 2
mv /data/data "$backup"
if [[ -d "$restore" ]]; then
    mv "$restore" /data/data
else
    mkdir /data/data
    printf '%s\n' "$target" > /data/TERMUX_ARCH
fi
printf '%s\n' "$target" > /data/TERMUX_ARCH
printf 'Switched staging from %s to %s; previous dependencies retained in %s\n' "$current" "$target" "$backup"

#!/usr/bin/env bash
set -euo pipefail

DIR="$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")"

"$DIR/generate.sh" \
    --project="poodle_async_mini" \
    --package="poodle_async_mini" \
    --version="4.0.0" \
    --whitelist="$DIR/whitelist.txt" \
    $@

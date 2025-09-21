#!/usr/bin/env bash
set -euo pipefail

DIR="$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")"

"$DIR/generate.sh" \
    --project="poodle_async_full" \
    --package="poodle_async_full" \
    $@

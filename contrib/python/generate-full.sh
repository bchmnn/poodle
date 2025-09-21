#!/usr/bin/env bash
set -euo pipefail

DIR="$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")"

"$DIR/generate.sh" \
    --project="poodle_async" \
    --package="poodle_async" \
    --version="4.0.0" \
    $@

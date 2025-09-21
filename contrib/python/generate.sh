#!/usr/bin/env bash
set -euo pipefail

# https://openapi-generator.tech/docs/globals/#available-global-properties
# https://openapi-generator.tech/docs/generators/python#config-options

OPENAPI_GENERATOR_CLI_VERSION="v7.15.0"
GENERATOR="python"
PACKAGE_URL="https://github.com/bchmnn/poodle"
GIT_USER_ID="bchmnn"
GIT_REPO_ID="poodle"

POS_ARGS=()
METHODS=""
WHITELIST=""
POODLE=""
MOODLE=""
MOODLE_DOCKER=""
PROJECT_NAME=""
PACKAGE_NAME=""
PACKAGE_VERSION=""
PACKAGE_BUILD=""
while [[ $# -gt 0 ]]; do
    case $1 in
    --poodle=*)
        POODLE="${1#*=}"
        shift
        ;;
    -p | --poodle)
        POODLE="$2"
        shift
        shift
        ;;
    --moodle=*)
        MOODLE="${1#*=}"
        shift
        ;;
    -m | --moodle)
        MOODLE="$2"
        shift
        shift
        ;;
    --moodle-docker=*)
        MOODLE_DOCKER="${1#*=}"
        shift
        ;;
    -d | --moodle-docker)
        MOODLE_DOCKER="$2"
        shift
        shift
        ;;
    --project=*)
        PROJECT_NAME="${1#*=}"
        shift
        ;;
    --package=*)
        PACKAGE_NAME="${1#*=}"
        shift
        ;;
    --version=*)
        PACKAGE_VERSION="${1#*=}"
        shift
        ;;
    --build=*)
        PACKAGE_BUILD="${1#*=}"
        shift
        ;;
    --methods=*)
        METHODS="${1#*=}"
        shift
        ;;
    --whitelist=*)
        WHITELIST="${1#*=}"
        shift
        ;;
    *)
        POS_ARGS+=("$1")
        shift
        ;;
    esac
done

set -- "${POS_ARGS[@]}"

OUT="$1"

DIR="$(dirname -- "$(realpath -- "${BASH_SOURCE[0]}")")"

if [[ "$METHODS" == "" ]]; then
    METHODS=$(mktemp -p "" methods.XXXXXXXXXX.json)

    "$POODLE" extract \
        -d "$MOODLE_DOCKER" \
        -o "$METHODS" \
        "$MOODLE"
fi

TEMPLATE=$(mktemp -dp "" template.XXXXXXXXXX)

"$POODLE" template \
    "$GENERATOR" \
    -di "$OPENAPI_GENERATOR_CLI_VERSION" \
    -p "$DIR/template.patch" \
    -o "$TEMPLATE"

SPEC=$(mktemp -p "" spec.XXXXXXXXXX.json)

if [[ "$WHITELIST" == "" ]]; then
    "$POODLE" convert \
        -m "$MOODLE" \
        --skip-add-tags \
        -o "$SPEC" \
        "$METHODS"
else
    "$POODLE" convert \
        -m "$MOODLE" \
        --whitelist "$DIR/whitelist.txt" \
        --skip-add-tags \
        -o "$SPEC" \
        "$METHODS"
fi

if [[ "$PACKAGE_BUILD" != "0" ]]; then
    PACKAGE_VERSION="$PACKAGE_VERSION.post$PACKAGE_BUILD"
fi

"$POODLE" generate \
    "$GENERATOR" \
    --parents -o "$OUT" \
    -di "$OPENAPI_GENERATOR_CLI_VERSION" \
    -t "$TEMPLATE" \
    --ignore-file-override="$DIR/openapi-generator-ignore" \
    -a "--global-property apiTests=false" \
    -a "--global-property modelTests=false" \
    -a "--global-property apiDocs=false" \
    -a "--global-property modelDocs=false" \
    -a "--additional-properties projectName=$PROJECT_NAME" \
    -a "--additional-properties packageName=$PACKAGE_NAME" \
    -a "--additional-properties packageVersion=$PACKAGE_VERSION" \
    -a "--additional-properties packageUrl=$PACKAGE_URL" \
    -a "--additional-properties library=asyncio" \
    -a "--git-user-id $GIT_USER_ID" \
    -a "--git-repo-id $GIT_REPO_ID" \
    "$SPEC"

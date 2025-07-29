#!/usr/bin/env bash

set -e
set -u

usage() {
    echo "Usage: $0 <moodle_dir> <moodle_docker_dir> [--outfile <file|GIT>] [--skip-setup-db]"
    exit 1
}

outfile=""
setup_db=true

if [[ $# -lt 2 ]]; then
    usage
fi

moodle_dir="$1"
docker_dir="$2"
shift 2

while [[ $# -gt 0 ]]; do
    case "$1" in
        --outfile)
            shift
            outfile="$1"
            ;;
        --skip-setup-db)
            setup_db=false
            ;;
        *)
            usage
            ;;
    esac
    shift
done

if [[ "$outfile" == "GIT" ]]; then
    if ! git -C "$moodle_dir" rev-parse --is-inside-work-tree &>/dev/null; then
        echo "Error: $moodle_dir is not a Git repository"
        exit 1
    fi

    tag=$(git -C "$moodle_dir" describe --exact-match --tags HEAD 2>/dev/null || true)
    if [[ -n "$tag" ]]; then
        outfile="webservices@${tag}.json"
    else
        commit_hash=$(git -C "$moodle_dir" rev-parse --short HEAD)
        outfile="webservices@${commit_hash}.json"
    fi
fi

temp=$(mktemp -d)
cleanup() {
    rm -rf "$temp"
}
trap cleanup EXIT

cp -r "$moodle_dir"/* "$temp/"
export MOODLE_DOCKER_WWWROOT="$temp"
cp export_webservices.php "$MOODLE_DOCKER_WWWROOT/admin/cli"
export MOODLE_DOCKER_DB=pgsql
cp "$docker_dir/config.docker-template.php" "$MOODLE_DOCKER_WWWROOT/config.php"

"$docker_dir/bin/moodle-docker-compose" up -d
"$docker_dir/bin/moodle-docker-wait-for-db"

if $setup_db; then
    "$docker_dir/bin/moodle-docker-compose" exec webserver php admin/cli/install_database.php --agree-license --adminpass="admin"
fi

if [[ -n "$outfile" ]]; then
    "$docker_dir/bin/moodle-docker-compose" exec webserver php admin/cli/export_webservices.php | tee "$outfile"
else
    "$docker_dir/bin/moodle-docker-compose" exec webserver php admin/cli/export_webservices.php
fi

"$docker_dir/bin/moodle-docker-compose" down

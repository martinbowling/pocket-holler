#!/bin/sh
set -eu
task_root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
task_node=${POCKETHOLLER_NODE:-/opt/homebrew/Cellar/node/26.5.0/bin/node}
task_cli=${POCKETHOLLER_CLI:-"$HOME/Library/Application Support/modretro-chromatic/toolchain/.local/vendor/gb-studio/out/cli/gb-studio-cli.js"}
mkdir -p "$task_root/dist"
exec "$task_node" "$task_cli" make:rom "$task_root/project.gbsproj" "$task_root/dist/PocketHoller-opening.gbc" --verbose

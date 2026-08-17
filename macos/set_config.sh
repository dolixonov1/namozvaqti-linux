#!/usr/bin/env bash
# Helper invoked by the xbar dropdown's settings rows (language, city,
# pre-alert, mute — see namozvaqti/scripts/xbar_plugin.py's `bash=` lines).
# Resolves the project root relative to its own location, so — unlike the
# other macos/ files — it needs no absolute-path placeholders filled in.
#
# Usage: set_config.sh <key> <value>   e.g. set_config.sh lang uz
set -u

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR" || exit 1

UV="$(command -v uv || echo /opt/homebrew/bin/uv)"
"$UV" run -m namozvaqti.scripts.set_config "${1:-}" "${2:-}"

#!/usr/bin/env bash
# xbar plugin — shows next prayer + countdown in the macOS menu bar.
#
# Setup:
#   1. Fill in the two placeholders below.
#   2. Copy this file into xbar's plugins folder:
#        cp macos/namozvaqti.60s.sh "$HOME/Library/Application Support/xbar/plugins/"
#   3. Make it executable:
#        chmod +x "$HOME/Library/Application Support/xbar/plugins/namozvaqti.60s.sh"
#   4. Open xbar (or "Refresh All" from its menu) — it re-runs this every 60s,
#      matching the self-healing poll interval used for Polybar in the README.
set -u

cd /ABSOLUTE/PATH/TO/namozvaqti-linux || exit 1
/ABSOLUTE/PATH/TO/uv run -m namozvaqti.scripts.xbar_plugin

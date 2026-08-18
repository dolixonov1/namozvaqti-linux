import json
import sys
import traceback
from datetime import datetime

# bare clock-history glyph used to flag stale (last-known) data on the bar; no
# accompanying word, to keep the label short.
STALE_MARKER = "󰅐"


def time_remaining(target_ts: int, now_ts: int):
    diff = max(0, int(target_ts - now_ts))

    hours = diff // 3600
    minutes = (diff % 3600) // 60

    return f"{hours}h {minutes}m"


def format_text(name, prayer, now_ts, translate=None, ramadan=False):
    remaining = time_remaining(prayer["timestamp"], now_ts)
    t = translate or {}
    label = t.get(name) or name.capitalize()
    # Ramadan mode: the bar counts down to iftar (maghrib) / suhoor-end (fajr)
    # under their own names instead of the plain prayer labels.
    if ramadan:
        if name == "maghrib":
            label = t.get("iftar", "Iftar")
        elif name == "fajr":
            label = t.get("suhoor", "Suhoor")
    return f"  {label} {prayer['time']} | 󰔟 {remaining}"  # 󰞌


def format_tooltip(day_data, translate=None):
    # full list shown on click (Ishroq included when present)
    order = ["fajr", "sunrise", "ishroq", "dhuhr", "asr", "maghrib", "isha"]

    lines = []
    for name in order:
        prayer = day_data.get(name)
        if not prayer:
            continue
        label = translate.get(name, name.capitalize()) if translate else name.capitalize()
        lines.append(f"{label:<9} {prayer['time']}")

    # hijri date (when the cached day carries it) heads the tooltip
    hijri = day_data.get("_hijri")
    if hijri:
        lines.insert(0, f"☪ {hijri}")

    return "\n".join(lines)


def build_waybar_output(translate=None):
    from namozvaqti.service import (
        get_day,
        get_next_prayer,
        next_prayer_for_day,
        rebuild_for_date,
    )

    now = datetime.now()
    now_ts = int(now.timestamp())

    # 1️⃣ normal path: today's data (cached, or fetched — 3 attempts in fetch.py)
    try:
        today_data = get_day(now)
        name, prayer = get_next_prayer(now)
        ramadan = today_data.get("_hijri_month") == 9
        return json.dumps(
            {
                "text": format_text(name, prayer, now_ts, translate, ramadan),
                "tooltip": format_tooltip(today_data, translate),
            }
        )
    except Exception as e:
        loading_error = str(e)
        # Surface the real cause on stderr (e.g. `prayer.sh 2>/tmp/prayer.log`).
        # Without this, a parser bug looks identical to being offline and the
        # bar silently shows stale data forever.
        traceback.print_exc(file=sys.stderr)

    # 2️⃣ offline (all attempts failed) → fall back to the last cached day,
    # re-stamped onto today's clock, flagged with a bare 󰅐 on the bar.
    from namozvaqti.cache import load_latest_before

    stale = load_latest_before(now)
    if stale is not None:
        day_key, day_data = stale
        approx = rebuild_for_date(day_data, now)
        name, prayer = next_prayer_for_day(approx, now)
        ramadan = day_data.get("_hijri_month") == 9
        return json.dumps(
            {
                "text": f"{STALE_MARKER} {format_text(name, prayer, now_ts, translate, ramadan)}",
                "tooltip": f"{format_tooltip(day_data, translate)}\n{STALE_MARKER} {day_key}",
            }
        )

    # 3️⃣ nothing cached at all → keep showing loading while it keeps retrying
    return json.dumps({"text": "󰔟 Loading...", "tooltip": loading_error})

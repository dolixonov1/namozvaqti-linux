from datetime import datetime

from namozvaqti.cache import load_day
from namozvaqti.time_utils import build_timestamp

# Order used to pick the "next" prayer and to lay out the tooltip. Sunrise and
# Ishroq are informational rows; they're included so the countdown also stops on
# them.
PRAYER_ORDER = ["fajr", "sunrise", "ishroq", "dhuhr", "asr", "maghrib", "isha"]


def ensure_day(date: datetime) -> dict:
    """Return one day's enriched prayer dict, fetching + caching if missing.

    Aladhan returns a whole month in one call, so a cache miss fetches the entire
    month and writes a per-day cache file for each day — one successful fetch
    then runs offline for the rest of the month. Done synchronously (it's a fast
    JSON call) to avoid the old daemon-thread bug where the one-shot
    waybar/polybar process exited before a background fetch could finish.
    """
    from namozvaqti.cache import save_day
    from namozvaqti.fetch import fetch_month
    from namozvaqti.parse import parse_month
    from namozvaqti.transform import enrich_with_timestamps

    cached = load_day(date)
    if cached is not None:
        return cached

    key = date.strftime("%Y-%m-%d")

    data = fetch_month(date.year, date.month)
    parsed = parse_month(data)                     # {date_key: {name: "HH:MM"}}
    enriched = enrich_with_timestamps(parsed)      # {date_key: {name: {time, ts}}}

    for day_key, day in enriched.items():
        save_day(day_key, day)

    if key not in enriched:
        raise RuntimeError(f"Fetched month had no entry for {key}")

    return enriched[key]


def get_day(date: datetime) -> dict:
    return ensure_day(date)


def next_prayer_for_day(day_data: dict, now: datetime):
    """Pick the next prayer from an already-loaded day dict (no fetching)."""
    now_ts = int(now.timestamp())

    # 1️⃣ next prayer still ahead today
    for name in PRAYER_ORDER:
        prayer = day_data.get(name)
        if prayer and prayer["timestamp"] > now_ts:
            return name, prayer

    # 2️⃣ after isha → tomorrow's fajr. praytime.uz is today-only, so approximate
    # it as today's fajr + 24h (a minute's drift at most; the page rolls over to
    # the new day after midnight and the real time is fetched then).
    fajr = day_data["fajr"]
    return "fajr", {"time": fajr["time"], "timestamp": fajr["timestamp"] + 86400}


def rebuild_for_date(day_data: dict, date: datetime) -> dict:
    """Re-stamp a day's time strings onto another date's clock.

    Used for the stale fallback: yesterday's "HH:MM" values are recomputed as
    today's timestamps so the live countdown still works (the times themselves
    drift only ~1 min/day).
    """
    key = date.strftime("%Y-%m-%d")
    return {
        name: (
            p  # "_"-prefixed metadata (hijri date etc.) — copy through as-is
            if name.startswith("_")
            else {"time": p["time"], "timestamp": build_timestamp(key, p["time"])}
        )
        for name, p in day_data.items()
    }


def get_next_prayer(now: datetime):
    return next_prayer_for_day(get_day(now), now)


def get_next_prayer_resilient(now: datetime):
    """Next prayer, with the same stale fallback the bar uses.

    Normally reads today's (cached or freshly fetched) data. If that fails
    (offline + today not cached), it falls back to the most recent cached day
    re-stamped onto today's clock — so callers like the scheduler still get a
    usable next prayer (and fire notifications) instead of an exception. Raises
    only when nothing is cached at all.
    """
    try:
        return next_prayer_for_day(get_day(now), now)
    except Exception:
        from namozvaqti.cache import load_latest_before

        stale = load_latest_before(now)
        if stale is None:
            raise
        _, day_data = stale
        approx = rebuild_for_date(day_data, now)
        return next_prayer_for_day(approx, now)

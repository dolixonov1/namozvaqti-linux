import subprocess
import sys
import time
from datetime import datetime

from namozvaqti.config import get_setting
from namozvaqti.lang import LANGS, STRINGS, get_lang
from namozvaqti.notify import notify
from namozvaqti.service import get_next_prayer_resilient

# Sleep in chunks (instead of one long sleep to the prayer time) so config
# changes made from the xbar menu — city, language, pre-alert minutes, mute —
# are picked up within a minute, and so the loop self-corrects after a
# laptop sleep/wake skews the wall clock.
POLL_CHUNK = 60

DEFAULT_PREALERT_MIN = 10


def send_waybar_signal():
    # Waybar (and the RTMIN+8 signal convention) is Linux/Wayland-only; there's
    # nothing to refresh on macOS, so skip the call instead of shelling out to a
    # pkill that can never match anything.
    if not sys.platform.startswith("linux"):
        return

    try:
        subprocess.run(["pkill", "-RTMIN+8", "waybar"], check=False)
    except Exception as e:
        print(f"[Waybar] Signal failed: {e}")


def _prealert_minutes() -> int:
    try:
        return max(0, int(get_setting("prealert", str(DEFAULT_PREALERT_MIN))))
    except (TypeError, ValueError):
        return DEFAULT_PREALERT_MIN


def run():
    last_pre_ts = None
    last_main_ts = None

    while True:
        now_ts = datetime.now().timestamp()

        try:
            # resilient: falls back to the last cached day (re-stamped onto
            # today) when offline, so notifications still fire on stale data.
            name, prayer = get_next_prayer_resilient(datetime.now())
        except Exception as e:
            # only reached when nothing is cached at all (never fetched offline)
            print(f"[Scheduler] Failed to get prayer time: {e}")
            time.sleep(60)
            continue

        target_ts = prayer["timestamp"]
        pre_min = _prealert_minutes()
        pre_ts = target_ts - pre_min * 60 if pre_min else None

        # pick the next pending event: the pre-alert (if enabled, still ahead
        # and not yet fired for this prayer) or the prayer itself
        if pre_ts and now_ts < pre_ts and last_pre_ts != target_ts:
            event, event_ts = "pre", pre_ts
        else:
            event, event_ts = "main", target_ts

        remaining = event_ts - now_ts
        if remaining > 2:
            time.sleep(min(remaining, POLL_CHUNK))
            continue
        if remaining > 0:
            time.sleep(remaining)

        # read language/mute at fire time so menu changes apply immediately
        lang = get_lang()
        label = LANGS[lang].get(name) or name.capitalize()
        s = STRINGS[lang]
        muted = get_setting("mute", "0") == "1"

        if event == "pre":
            if last_pre_ts != target_ts:
                notify(
                    title=s["pre_title"].format(name=label),
                    message=s["pre_msg"].format(
                        name=label, min=pre_min, time=prayer["time"]
                    ),
                    silent=True,  # gentle heads-up: banner only, no adhan sound
                )
                last_pre_ts = target_ts
        else:
            if last_main_ts != target_ts:
                notify(
                    title=s["time_title"].format(name=label),
                    message=prayer["time"],
                    silent=muted,
                )
                send_waybar_signal()
                last_main_ts = target_ts

            # small buffer so the next loop sees this prayer as past
            time.sleep(5)


if __name__ == "__main__":
    run()

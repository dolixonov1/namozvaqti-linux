import subprocess
import sys
import time
from datetime import datetime

from namozvaqti.notify import notify
from namozvaqti.service import get_next_prayer_resilient


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


def run():
    last_notified_ts = None

    while True:
        now = datetime.now()

        try:
            # resilient: falls back to the last cached day (re-stamped onto
            # today) when offline, so notifications still fire on stale data.
            name, prayer = get_next_prayer_resilient(now)
            prayer_time = datetime.fromtimestamp(prayer["timestamp"])
        except Exception as e:
            # only reached when nothing is cached at all (never fetched offline)
            print(f"[Scheduler] Failed to get prayer time: {e}")
            time.sleep(60)
            continue

        wait_seconds = max(0, (prayer_time - now).total_seconds())

        if wait_seconds > 0:
            time.sleep(wait_seconds)

        # Prevent duplicate notifications
        if last_notified_ts != prayer["timestamp"]:
            notify(
                title=f"{name} time",
                message=prayer_time.strftime("%H:%M"),
            )
            send_waybar_signal()
            last_notified_ts = prayer["timestamp"]

        # small buffer to avoid re-trigger
        time.sleep(5)


if __name__ == "__main__":
    run()

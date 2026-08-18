import time

import requests

from namozvaqti.cities import CITIES, get_city

# Prayer times are computed via the Aladhan API, configured to reproduce the
# official ISLOM.UZ (Muslim Board of Uzbekistan) calendar. Verified against the
# official June-2026 Namangan sheet: every prayer matches to within 1 minute
# (rounding) with the settings below. The angle/tune settings are the board's
# country-wide method, so they apply to every city in cities.py; only the
# coordinates change with the selected city.
#
#   method=99           -> custom angle-based method
#   methodSettings      -> Fajr 15.5°, Maghrib = sunset (default), Isha 15.5°
#   school=1            -> Hanafi Asr (later Asr), as used across Uzbekistan
#   tune                -> +4 min on Maghrib (the board's post-sunset margin)
#
# tune field order is: Imsak,Fajr,Sunrise,Dhuhr,Asr,Maghrib,Sunset,Isha,Midnight


def _params() -> dict:
    city = CITIES[get_city()]
    return {
        "latitude": city["lat"],
        "longitude": city["lng"],
        "method": 99,
        "methodSettings": "15.5,null,15.5",
        "school": 1,
        "timezonestring": "Asia/Tashkent",
        "tune": "0,0,0,0,0,4,0,0,0",
    }


def fetch_month(year: int, month: int) -> list[dict]:
    """Fetch one month of prayer times for the configured city from Aladhan.

    Returns the API's ``data`` array (one entry per day). Aladhan serves a whole
    month in a single call, so one successful fetch is enough to run offline for
    the rest of the month (see ``service.ensure_day``, which caches every day).
    """
    url = f"https://api.aladhan.com/v1/calendar/{year}/{month}"

    # 3 attempts with short timeouts so an offline poll fails fast (~24s worst
    # case) instead of hanging the polybar module; after this the caller falls
    # back to the last cached day (marked stale).
    attempts = 3
    delay = 1

    for i in range(attempts):
        try:
            res = requests.get(url, params=_params(), timeout=8)
            res.raise_for_status()
            data = res.json().get("data")
            if not data:
                raise RuntimeError("Aladhan response missing 'data'")
            return data

        except requests.RequestException as e:
            if i == attempts - 1:
                raise e  # final failure
            time.sleep(delay * (i + 1))  # linear backoff

    # satisfies type checker (even though unreachable)
    raise RuntimeError("Unreachable: fetch_month exhausted retries")

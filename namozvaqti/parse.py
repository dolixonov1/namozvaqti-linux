# Map Aladhan timing keys -> the internal english keys the rest of the pipeline
# expects. Ishroq isn't returned by Aladhan; it's derived as Sunrise + 20 min,
# which matches the ISLOM.UZ sheet exactly. Tahajjud is intentionally omitted —
# the official sheet's Tahajjud has no reliable Aladhan equivalent (its offset
# from Midnight/Lastthird drifts), so showing it would mislead.
ALADHAN_KEYS = {
    "Fajr": "fajr",
    "Sunrise": "sunrise",
    "Dhuhr": "dhuhr",
    "Asr": "asr",
    "Maghrib": "maghrib",
    "Isha": "isha",
}

ISHROQ_OFFSET_MIN = 20


def _clean(t: str) -> str:
    # Aladhan formats times like "04:44 (+05)" -> keep just "HH:MM".
    return t.split(" ")[0]


def _add_minutes(hhmm: str, minutes: int) -> str:
    h, m = map(int, hhmm.split(":"))
    total = (h * 60 + m + minutes) % (24 * 60)
    return f"{total // 60:02d}:{total % 60:02d}"


def parse_month(data: list[dict]) -> dict:
    """Parse Aladhan's monthly ``data`` array into {YYYY-MM-DD: {name: "HH:MM"}}.

    Each entry carries a gregorian date and a ``timings`` dict; we keep the six
    core prayers and derive Ishroq from Sunrise.
    """
    result = {}

    for day in data:
        d, mo, y = day["date"]["gregorian"]["date"].split("-")  # "DD-MM-YYYY"
        key = f"{y}-{mo}-{d}"

        timings = day["timings"]
        prayers = {
            en: _clean(timings[al]) for al, en in ALADHAN_KEYS.items() if al in timings
        }

        if "sunrise" in prayers:
            prayers["ishroq"] = _add_minutes(prayers["sunrise"], ISHROQ_OFFSET_MIN)

        # hijri date rides along under "_"-prefixed keys, which the rest of the
        # pipeline (transform/service/format) passes through untouched; month
        # number 9 (Ramadan) also drives the iftar/suhoor labels in format.py.
        hijri = day.get("date", {}).get("hijri") or {}
        try:
            prayers["_hijri"] = (
                f'{hijri["day"]} {hijri["month"]["en"]} {hijri["year"]}'
            )
            prayers["_hijri_month"] = int(hijri["month"]["number"])
        except (KeyError, TypeError, ValueError):
            pass

        result[key] = prayers

    if not result:
        raise RuntimeError("Parsed data is empty")

    return result

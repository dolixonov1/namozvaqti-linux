from namozvaqti.time_utils import build_timestamp


def enrich_with_timestamps(parsed: dict) -> dict:
    result = {}

    for date, prayers in parsed.items():
        result[date] = {}

        for name, time_str in prayers.items():
            # "_"-prefixed metadata (hijri date etc.) isn't a prayer time —
            # copy it through untouched.
            if name.startswith("_"):
                result[date][name] = time_str
                continue

            key = name.lower()

            result[date][key] = {
                "time": time_str,
                "timestamp": build_timestamp(date, time_str),
            }

    return result

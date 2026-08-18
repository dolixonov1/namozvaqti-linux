import sys

from namozvaqti.cities import CITIES
from namozvaqti.config import get_setting, set_setting
from namozvaqti.lang import LANGS

# Values the xbar menu is allowed to write; anything else is ignored so a
# malformed click can't corrupt the config.
VALID = {
    "lang": lambda v: v in LANGS,
    "city": lambda v: v in CITIES,
    "prealert": lambda v: v in ("0", "5", "10", "15"),
    "mute": lambda v: v in ("0", "1", "toggle"),
}


def main():
    if len(sys.argv) < 3:
        return

    key, value = sys.argv[1], sys.argv[2]

    check = VALID.get(key)
    if not check or not check(value):
        return

    if key == "mute" and value == "toggle":
        value = "0" if get_setting("mute", "0") == "1" else "1"

    set_setting(key, value)


if __name__ == "__main__":
    main()

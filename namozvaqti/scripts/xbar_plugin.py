import json
from datetime import datetime, timedelta
from pathlib import Path

from namozvaqti.cache import load_day
from namozvaqti.cities import CITIES, get_city
from namozvaqti.config import get_setting
from namozvaqti.format import build_waybar_output
from namozvaqti.lang import LANG_LABELS, LANGS, STRINGS, get_lang
from namozvaqti.qibla import qibla_direction
from namozvaqti.service import PRAYER_ORDER

SET_CONFIG = Path(__file__).resolve().parents[2] / "macos" / "set_config.sh"

FONT = 'font="Hack Nerd Font"'
BOLD = 'font="Hack Nerd Font Bold"'


def config_row(text: str, key: str, value: str, checked: bool = False, depth: int = 1):
    """A submenu row that writes one setting and immediately re-renders xbar."""
    dashes = "--" * depth
    mark = "✓ " if checked else "    "
    print(
        f'{dashes}{mark}{text} | bash="{SET_CONFIG}" param1={key} param2={value} '
        f"terminal=false refresh=true"
    )


def weekly_schedule(lang: str):
    """Submenu with the next 7 days, read straight from the per-day cache.

    ensure_day (already run by build_waybar_output) caches the whole month on
    any fetch, so these are pure local reads; days spilling into a not-yet-
    fetched next month are simply skipped.
    """
    s = STRINGS[lang]
    translate = LANGS[lang]

    print(s["schedule"])
    today = datetime.now()
    for i in range(7):
        d = today + timedelta(days=i)
        day = load_day(d)
        if not day:
            continue
        print(f"--{d.strftime('%d.%m')} {s['weekdays'][d.weekday()]}")
        for name in PRAYER_ORDER:
            p = day.get(name)
            if not p:
                continue
            label = translate.get(name) or name.capitalize()
            print(f"----{label:<9} {p['time']} | {FONT}")


def main():
    """Convert the shared Waybar-style JSON into xbar's plain-text plugin format.

    xbar reads: <menu bar title>\\n---\\n<dropdown line>\\n<dropdown line>...

    xbar reserves " | " on a line to introduce styling params (e.g. "Title |
    color=red") and this build has no working escape for a literal "|" in the
    title (confirmed: both "\\|" and "||" still get parsed as the params
    delimiter and error out). format.py's title uses " | " as a plain visual
    separator between the prayer name/time and the countdown, so swap it for
    "│" (U+2502 box-drawing vertical bar) — visually a near-identical column
    divider, but a distinct character the parser won't touch.
    """
    lang = get_lang()
    s = STRINGS[lang]
    city = get_city()

    data = json.loads(build_waybar_output(translate=LANGS[lang]))

    title = data.get("text", "Namoz").replace(" | ", " │ ")
    # Nerd Font renders the  /  glyphs; Bold variant = bold weight.
    print(f"{title} | {BOLD} color=#FF7A1B")
    print("---")

    # today's times (+ hijri date line when cached) — monospace for alignment
    for line in data.get("tooltip", "").splitlines():
        if line:
            print(f"{line} | {FONT}")

    deg = qibla_direction(CITIES[city]["lat"], CITIES[city]["lng"])
    print(f'{s["qibla"]}: {deg:.0f}°')
    print("---")

    weekly_schedule(lang)
    print("---")

    # settings: language / city / pre-alert / sound
    print(f'{s["language"]}: {LANG_LABELS[lang]}')
    for code, lang_label in LANG_LABELS.items():
        config_row(lang_label, "lang", code, checked=(code == lang))

    print(f'{s["city"]}: {CITIES[city]["label"]}')
    for code, info in CITIES.items():
        config_row(info["label"], "city", code, checked=(code == city))

    pre = get_setting("prealert", "10")
    pre_label = s["off"] if pre == "0" else f'{pre} {s["minutes"]}'
    print(f'{s["prealert"]}: {pre_label}')
    config_row(s["off"], "prealert", "0", checked=(pre == "0"))
    for minutes in ("5", "10", "15"):
        config_row(
            f'{minutes} {s["minutes"]}', "prealert", minutes, checked=(pre == minutes)
        )

    muted = get_setting("mute", "0") == "1"
    sound_label = s["sound_off"] if muted else s["sound_on"]
    print(
        f'{sound_label} | bash="{SET_CONFIG}" param1=mute param2=toggle '
        f"terminal=false refresh=true"
    )


if __name__ == "__main__":
    main()

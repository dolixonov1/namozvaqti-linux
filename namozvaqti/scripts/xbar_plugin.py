import json

from namozvaqti.format import build_waybar_output


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
    data = json.loads(build_waybar_output())

    title = data.get("text", "Namoz").replace(" | ", " │ ")
    # font= renders the  /  glyphs correctly; without a Nerd Font installed
    # (e.g. `brew install --cask font-hack-nerd-font`) they show as tofu boxes.
    # The "Bold" variant gives a bold weight (xbar has no separate weight=).
    print(f'{title} | font="Hack Nerd Font Bold" color=#FF7A1B')
    print("---")

    tooltip = data.get("tooltip", "")
    for line in tooltip.splitlines():
        if line:
            print(line)


if __name__ == "__main__":
    main()

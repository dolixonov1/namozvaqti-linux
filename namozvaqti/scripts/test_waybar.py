from namozvaqti.format import build_waybar_output
from namozvaqti.lang import LANGS, get_lang

if __name__ == "__main__":
    # same language selection the xbar plugin uses (~/.config/namozvaqti/lang),
    # so Waybar/Polybar on Linux follow the configured language too
    print(build_waybar_output(translate=LANGS[get_lang()]))

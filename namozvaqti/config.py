from pathlib import Path

# One plain-text file per setting (lang, city, mute, prealert) under
# ~/.config/namozvaqti/ — trivially inspectable/editable by hand, and each
# read is a fresh stat so long-running processes (the scheduler) and the
# 60s xbar poll pick up changes made by the other without any signalling.
CONFIG_DIR = Path.home() / ".config" / "namozvaqti"


def get_setting(key: str, default: str | None = None) -> str | None:
    try:
        return (CONFIG_DIR / key).read_text().strip()
    except (FileNotFoundError, OSError):
        return default


def set_setting(key: str, value: str):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    (CONFIG_DIR / key).write_text(value)

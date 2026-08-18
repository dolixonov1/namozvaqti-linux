import os
import subprocess
import sys
from pathlib import Path

IS_MACOS = sys.platform == "darwin"

DEFAULT_SOUND = (
    Path(__file__).resolve().parent.parent / "assets" / "prayer-notification.wav"
)

DEFAULT_ICON = (
    Path(__file__).resolve().parent.parent / "assets" / "mosque_transparent.png"
)


def _play_sound(sound_path: Path | str | None, volume: float = 1.0):
    """
    Play sound using PipeWire (pw-play) on Linux, or afplay on macOS.

    Args:
        sound_path: Path to audio file
        volume: Volume level 0.0 to 1.0 (default: 1.0 = 100%)
    """
    if not sound_path:
        return

    try:
        p = Path(sound_path)
        if not p.exists():
            print(f"[Notification] Sound file not found: {p}")
            return

        if IS_MACOS:
            # afplay takes volume directly, no env var needed.
            subprocess.Popen(["afplay", "-v", str(volume), str(p)])
        else:
            # PipeWire volume control via environment variable
            # PIPEWIRE_VOLUME: 0.0 (mute) to 1.0 (100%)
            env = {"PIPEWIRE_VOLUME": str(volume)}
            subprocess.Popen(["pw-play", str(p)], env={**os.environ, **env})
    except Exception as e:
        print(f"[Notification] Failed to play sound: {e}")


def _escape_applescript(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def _notify_macos(title: str, message: str, silent: bool = False):
    # osascript's "display notification" has no --icon/--app-name/--urgency
    # equivalent to notify-send; it just shows up under whatever process ran
    # osascript. "sound name" with no argument plays the user's default
    # notification sound (System Settings > Notifications) instead of a
    # bundled custom wav.
    script = (
        f'display notification "{_escape_applescript(message)}" '
        f'with title "{_escape_applescript(title)}"'
    )
    if not silent:
        script += ' sound name "default"'
    subprocess.run(["osascript", "-e", script], check=False)


def _notify_linux(
    title: str,
    message: str,
    urgency: str,
    icon: Path | str | None,
    app_name: str,
    expire_time: int,
):
    cmd = [
        "notify-send",
        f"--app-name={app_name}",
        f"--urgency={urgency}",
        f"--expire-time={expire_time}",
        f"--icon={icon or DEFAULT_ICON}",
        title,
        message,
    ]
    subprocess.run(cmd, check=False)


def notify(
    title: str,
    message: str,
    sound: Path | str | None = None,
    volume: float = 1.0,
    urgency: str = "critical",
    icon: Path | str | None = None,
    app_name: str = "Prayer Times  ",
    expire_time: int = 0,
    silent: bool = False,
):
    """
    Show a desktop notification with sound.

    Args:
        title: Notification title
        message: Notification body
        sound: Path to sound file (None = use default)
        volume: Sound volume 0.0-1.0 (default: 1.0)
        urgency: 'low', 'normal', or 'critical' (default: 'critical'; Linux only)
        icon: Icon name or path (default: None = system default; Linux only)
        app_name: Application name shown in notification (Linux only)
        expire_time: Milliseconds before auto-dismiss (0 = never; Linux only)
        silent: Skip the sound (banner only) — used for pre-alerts and mute mode
    """
    try:
        if IS_MACOS:
            # no .title(): titles are already localized/cased by the caller,
            # and .title() mangles uz/ru text ("o'chiq" -> "O'Chiq")
            _notify_macos(title, message, silent=silent)
        else:
            _notify_linux(title, message, urgency, icon, app_name, expire_time)
    except Exception as e:
        print(f"[Notification] Failed to send notification: {e}")

    if silent or IS_MACOS:
        # macOS: "sound name" on the notification itself already played the
        # user's system-default sound — no separate custom wav on top of it.
        return

    # Play sound (fire-and-forget) — Linux only, via the bundled wav
    try:
        _play_sound(sound or DEFAULT_SOUND, volume=volume)
    except Exception as e:
        print(f"[Notification] Sound playback error: {e}")

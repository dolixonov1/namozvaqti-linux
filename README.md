# 🕌 NamozVaqti (Polybar / Waybar Prayer Times)

A lightweight Linux prayer-time system for **Namangan, Uzbekistan**:

* 📊 Polybar / Waybar integration (live next prayer + full-day list)
* 🔔 Desktop notifications (with sound) exactly at prayer time
* ⚡ Event-driven scheduler (sleeps until the next prayer — not polling-heavy)
* 💾 Monthly caching, offline-first (one fetch covers the whole month)

---

## 🧭 Data source

Prayer times come from the **[Aladhan API](https://aladhan.com/prayer-times-api)**,
configured to reproduce the **official ISLOM.UZ (Muslim Board of Uzbekistan)
Namangan calendar**. The parameters were reverse-engineered against the official
June-2026 sheet and match every prayer to within 1 minute (rounding):

| Parameter        | Value                  | Meaning                                   |
| ---------------- | ---------------------- | ----------------------------------------- |
| `latitude`       | `41.0058`              | Namangan                                  |
| `longitude`      | `71.6436`              | Namangan                                  |
| `method`         | `99`                   | Custom angle-based method                 |
| `methodSettings` | `15.5,null,15.5`       | Fajr 15.5° · Maghrib = sunset · Isha 15.5°|
| `school`         | `1`                    | Hanafi Asr (later Asr)                    |
| `timezonestring` | `Asia/Tashkent`        | UTC+5                                      |
| `tune`           | `0,0,0,0,0,4,0,0,0`    | +4 min on Maghrib (board's sunset margin) |

> **Ishroq** is derived as Sunrise + 20 min (matches the sheet exactly).
> **Tahajjud** is intentionally omitted — its value on the official sheet has no
> reliable Aladhan equivalent, so showing it would mislead.

All settings live in `namozvaqti/fetch.py`. To target another city, change the
coordinates (and re-verify `methodSettings`/`tune` against that region's sheet).

---

## 📦 Features

* Next prayer on the bar:

  ```
   Asr 17:29 | 󰔟 1h 30m
  ```

* Full day in the tooltip / click-popup:

  ```
  Fajr      02:56
  Sunrise   04:41
  Ishroq    05:01
  Dhuhr     12:14
  Asr       17:29
  Maghrib   19:52
  Isha      21:32
  ```

* Notification + sound at each prayer, with an instant bar refresh via signal.

* Stale data (offline) is flagged with a 󰅐 marker until the next successful fetch.

---

## 📁 Project Structure

```
namozvaqti/
├── fetch.py        # Aladhan API call (one month per request)
├── parse.py        # Aladhan JSON  → {date: {name: "HH:MM"}}  (+ Ishroq)
├── transform.py    # adds unix timestamps
├── cache.py        # per-day cache files in ~/.cache/namozvaqti/
├── service.py      # ensure/get day, pick next prayer, stale fallback
├── format.py       # builds the Polybar/Waybar JSON
├── notify.py       # desktop notification + sound
├── scheduler.py    # sleeps to next prayer → notify + signal bar
├── time_utils.py   # timezone-aware timestamp helper
├── scripts/
│   ├── test_waybar.py   # the bar entry point (prints the JSON)
│   └── test_notify.py   # manual notification test
└── assets/
    ├── prayer-notification.wav
    └── mosque_transparent.png
```

---

## ⚙️ Requirements

```bash
sudo nala install python3 libnotify-bin pipewire   # + polybar or waybar, jq
```

Python deps (only `requests`) are managed with **[uv](https://docs.astral.sh/uv/)**:

```bash
uv sync
```

---

## 🚀 Setup

### 1. Clone & sync

```bash
git clone https://github.com/MuhammadAkbar007/namozvaqti-linux.git
cd namozvaqti-linux
uv sync
```

### 2. Test the producer manually

```bash
uv run -m namozvaqti.scripts.test_waybar
```

Expected (Waybar-style JSON, consumed by both bars):

```json
{"text": "  Asr 17:29 | 󰔟 1h 30m", "tooltip": "Fajr 02:56\n..."}
```

---

## 🧩 Bar Integration

The producer outputs **Waybar-style JSON**; Polybar consumes the same output via
a tiny `jq` wrapper.

### Shared producer — `~/.config/waybar/prayer.sh`

```bash
#!/usr/bin/env bash
cd /home/akbar/akbarDev/pet-projects/namozvaqti || exit 1
/home/akbar/.local/bin/uv run -m namozvaqti.scripts.test_waybar
```

### Polybar

`~/.config/polybar/prayer.sh` (extracts `.text`):

```bash
#!/usr/bin/env bash
set -u
out="$(~/.config/waybar/prayer.sh 2>/dev/null)"
[ -n "$out" ] && printf '%s\n' "$out" | jq -r '.text // empty'
```

`config.ini`:

```ini
[module/prayer]
type = custom/script
exec = ~/.config/polybar/prayer.sh
interval = 60
click-left = kitty -e ~/.config/polybar/prayer_popup.sh
```

> `interval = 60` also makes the bar **self-heal**: whenever today isn't cached
> (e.g. you were offline at boot), each poll retries the fetch, so the stale
> marker clears within ~60s of reconnecting.

### Waybar

`custom.jsonc`:

```json
"custom/prayer": {
    "exec": "~/.config/waybar/prayer.sh",
    "return-type": "json",
    "signal": 8,
    "tooltip": true
}
```

---

## 🔔 Scheduler (notifications + bar signal)

Test manually:

```bash
uv run -m namozvaqti.scheduler
```

`~/.config/systemd/user/namozvaqti.service`:

```ini
[Unit]
Description=Namoz Vaqti Scheduler
After=network.target

[Service]
ExecStart=/home/akbar/.local/bin/uv run -m namozvaqti.scheduler
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
```

Enable:

```bash
systemctl --user daemon-reload
systemctl --user enable --now namozvaqti.service
systemctl --user status namozvaqti.service
```

---

## ⚡ How It Works

```
fetch (1 month) → parse → transform → cache (per day) → service → bar / scheduler
```

1. **First run / cache miss** — fetches the whole month from Aladhan and writes
   one file per day to `~/.cache/namozvaqti/YYYY-MM-DD.json`. One successful
   fetch then runs **fully offline** for the rest of the month.
2. **Each prayer** — the scheduler sleeps until the next timestamp, sends a
   notification + sound, and signals the bar to refresh instantly.
3. **Bar** — re-renders on its 60s interval (Polybar) or on signal (Waybar).

---

## 🌐 Offline Behavior

| Scenario                          | Behavior                                            |
| --------------------------------- | --------------------------------------------------- |
| Current month cached              | ✅ Works fully offline                               |
| New month, offline                | Shows the last cached day, flagged 󰅐 (stale)        |
| Reconnected                       | Next 60s poll re-fetches the month; marker clears   |

---

## 🧪 Debugging

The bar producer prints real errors to **stderr** (a fetch/parse failure is no
longer silently hidden behind stale data):

```bash
~/.config/waybar/prayer.sh 2> /tmp/prayer.log
cat /tmp/prayer.log
```

Notifications / sound:

```bash
notify-send "Test" "Hello"
pw-play assets/prayer-notification.wav
```

---

## 🍎 Running on macOS

The fetch/cache/scheduler pipeline is plain Python (`requests` only), so it
runs unmodified on macOS. `notify.py` and `scheduler.py`'s bar-signal call
auto-detect the platform (`sys.platform`) and switch implementations — no
config needed.

| Piece                  | Linux                    | macOS                                    |
| ----------------------- | ------------------------- | ----------------------------------------- |
| Notifications            | `notify-send`              | `osascript -e 'display notification …'`   |
| Sound                     | `pw-play` (PipeWire)        | `afplay`                                    |
| Bar refresh signal      | `pkill -RTMIN+8 waybar`   | skipped (no Waybar on macOS)             |
| Autostart               | systemd user service       | launchd agent                              |

### 1. Install `uv`

```bash
brew install uv
```

`afplay` and `osascript` are already built into macOS — nothing else to
install for notifications/sound.

### 2. Clone & sync

```bash
git clone https://github.com/MuhammadAkbar007/namozvaqti-linux.git
cd namozvaqti-linux
uv sync
```

`uv` downloads its own Python 3.13 to satisfy `requires-python`, independent
of whatever `python3` is already on your `PATH`.

### 3. Test notifications & scheduler manually

```bash
uv run -m namozvaqti.scripts.test_notify   # should pop a notification + play sound
uv run -m namozvaqti.scheduler             # runs the same event loop as on Linux
```

### 4. Menu bar integration (optional, via xbar)

Polybar/Waybar don't exist on macOS. [xbar](https://xbarapp.com/) is the
closest equivalent — it runs a script on an interval and shows its output in
the menu bar. `namozvaqti/scripts/xbar_plugin.py` converts the same
Waybar-style JSON (`namozvaqti/format.py`) into xbar's plain-text plugin
format, so both bars stay driven by one source of truth.

```bash
brew install --cask xbar
```

Launch xbar once (it'll ask to create `~/Library/Application Support/xbar/plugins/`
and prompt for Accessibility/notification permissions), then:

```bash
cp macos/namozvaqti.60s.sh "$HOME/Library/Application Support/xbar/plugins/"
chmod +x "$HOME/Library/Application Support/xbar/plugins/namozvaqti.60s.sh"
```

Edit the two placeholders inside that copied file (project directory and
`which uv`), then refresh xbar (menu bar icon → "Refresh All") — it re-runs
the script every 60s (the `.60s.` in the filename), matching the Polybar
self-heal interval from the README above.

> The  /󰔟 glyphs come from a [Nerd Font](https://www.nerdfonts.com/); without
> one installed they'll render as boxes/tofu in the menu bar. Install one
> (e.g. `brew install --cask font-hack-nerd-font`) and set it as xbar's font
> via a `| font=Hack Nerd Font` suffix on the title line in
> `xbar_plugin.py` if you want the icons to show correctly — otherwise the
> text is still fully readable without them.

Without a bar, the scheduler alone still gives you notifications + sound at
each prayer time.

### 5. Autostart with launchd (instead of systemd)

Use [`macos/com.namozvaqti.scheduler.plist`](macos/com.namozvaqti.scheduler.plist)
in place of the systemd unit above — fill in the two absolute-path
placeholders (project directory and `which uv`), then:

```bash
cp macos/com.namozvaqti.scheduler.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.namozvaqti.scheduler.plist
launchctl kickstart -k gui/$(id -u)/com.namozvaqti.scheduler
launchctl print gui/$(id -u)/com.namozvaqti.scheduler   # check status
```

To stop/remove:

```bash
launchctl bootout gui/$(id -u)/com.namozvaqti.scheduler
```

### 6. Settings (xbar dropdown / config files)

The xbar dropdown has a settings section; every row just writes a plain-text
file under `~/.config/namozvaqti/`, so the same settings also work on Linux
(Waybar/Polybar read the language too) or can be set by hand:

| Setting | File | Values | Default |
|---|---|---|---|
| Language (UI + prayer names) | `lang` | `uz` / `ru` / `en` | `en` |
| City (all UZ regional centers) | `city` | `tashkent`, `namangan`, `andijan`, … see `namozvaqti/cities.py` | `namangan` |
| Pre-prayer reminder | `prealert` | minutes before the prayer, `0` = off | `10` |
| Mute (banner only, no adhan) | `mute` | `0` / `1` | `0` |

Both the scheduler and the bar re-read these on every cycle — no restarts
needed. The per-day cache is kept per city (`~/.cache/namozvaqti/<city>/`).

The dropdown also shows the Hijri date, the qibla bearing (computed offline),
and a 7-day schedule submenu. During Ramadan the menu bar counts down to
iftar/suhoor under their own labels instead of Maghrib/Fajr.

---

## ✍️ Author

Created by [Akbar](https://github.com/MuhammadAkbar007).

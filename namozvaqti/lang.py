from namozvaqti.config import get_setting, set_setting

DEFAULT_LANG = "en"

# Prayer-name translations. "iftar"/"suhoor" are the Ramadan-mode labels shown
# instead of maghrib/fajr while the hijri month is Ramadan (see format.py).
LANGS = {
    "en": {
        "fajr": "Fajr",
        "sunrise": "Sunrise",
        "ishroq": "Ishroq",
        "dhuhr": "Dhuhr",
        "asr": "Asr",
        "maghrib": "Maghrib",
        "isha": "Isha",
        "iftar": "Iftar",
        "suhoor": "Suhoor",
    },
    "uz": {
        "fajr": "Bomdod",
        "sunrise": "Quyosh",
        "ishroq": "Ishroq",
        "dhuhr": "Peshin",
        "asr": "Asr",
        "maghrib": "Shom",
        "isha": "Xufton",
        "iftar": "Iftorlik",
        "suhoor": "Saharlik",
    },
    "ru": {
        "fajr": "Фаджр",
        "sunrise": "Восход",
        "ishroq": "Ишрак",
        "dhuhr": "Зухр",
        "asr": "Аср",
        "maghrib": "Магриб",
        "isha": "Иша",
        "iftar": "Ифтар",
        "suhoor": "Сухур",
    },
}

LANG_LABELS = {
    "uz": "🇺🇿 Oʻzbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}

# UI strings for the xbar dropdown and scheduler notifications. str.format
# ignores unused kwargs, so every template may receive name/min/time.
STRINGS = {
    "en": {
        "time_title": "{name} time",
        "pre_title": "{name} soon",
        "pre_msg": "{name} in {min} min ({time})",
        "schedule": "📅 Weekly schedule",
        "language": "🌐 Language",
        "city": "🏙 City",
        "prealert": "⏰ Reminder",
        "off": "Off",
        "minutes": "min",
        "sound_on": "🔊 Sound: on",
        "sound_off": "🔇 Sound: off",
        "qibla": "🧭 Qibla",
        "weekdays": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
    },
    "uz": {
        "time_title": "{name} vaqti",
        "pre_title": "{name} yaqinlashdi",
        "pre_msg": "{min} daqiqa qoldi ({time})",
        "schedule": "📅 Haftalik jadval",
        "language": "🌐 Til",
        "city": "🏙 Shahar",
        "prealert": "⏰ Eslatma",
        "off": "O'chirilgan",
        "minutes": "daqiqa",
        "sound_on": "🔊 Ovoz: yoniq",
        "sound_off": "🔇 Ovoz: o'chiq",
        "qibla": "🧭 Qibla",
        "weekdays": ["Dush", "Sesh", "Chor", "Pay", "Jum", "Shan", "Yak"],
    },
    "ru": {
        "time_title": "Время {name}",
        "pre_title": "Скоро {name}",
        "pre_msg": "Осталось {min} мин ({time})",
        "schedule": "📅 Расписание недели",
        "language": "🌐 Язык",
        "city": "🏙 Город",
        "prealert": "⏰ Напоминание",
        "off": "Выкл",
        "minutes": "мин",
        "sound_on": "🔊 Звук: вкл",
        "sound_off": "🔇 Звук: выкл",
        "qibla": "🧭 Кибла",
        "weekdays": ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"],
    },
}


def get_lang() -> str:
    code = get_setting("lang", DEFAULT_LANG)
    return code if code in LANGS else DEFAULT_LANG


def set_lang(code: str):
    if code in LANGS:
        set_setting("lang", code)

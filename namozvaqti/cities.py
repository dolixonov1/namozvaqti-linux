from namozvaqti.config import get_setting, set_setting

DEFAULT_CITY = "namangan"

# Regional centers of Uzbekistan. All share Asia/Tashkent and the same Muslim
# Board calculation settings (see fetch.py) — only the coordinates differ.
CITIES = {
    "tashkent": {"label": "Toshkent", "lat": 41.2995, "lng": 69.2401},
    "namangan": {"label": "Namangan", "lat": 41.0058, "lng": 71.6436},
    "andijan": {"label": "Andijon", "lat": 40.7821, "lng": 72.3442},
    "fergana": {"label": "Farg'ona", "lat": 40.3894, "lng": 71.7789},
    "samarkand": {"label": "Samarqand", "lat": 39.6542, "lng": 66.9597},
    "bukhara": {"label": "Buxoro", "lat": 39.7747, "lng": 64.4286},
    "urgench": {"label": "Urganch", "lat": 41.5506, "lng": 60.6314},
    "nukus": {"label": "Nukus", "lat": 42.4531, "lng": 59.6103},
    "qarshi": {"label": "Qarshi", "lat": 38.8606, "lng": 65.7891},
    "termez": {"label": "Termiz", "lat": 37.2242, "lng": 67.2783},
    "jizzakh": {"label": "Jizzax", "lat": 40.1158, "lng": 67.8422},
    "navoiy": {"label": "Navoiy", "lat": 40.0844, "lng": 65.3792},
    "gulistan": {"label": "Guliston", "lat": 40.4897, "lng": 68.7842},
}


def get_city() -> str:
    code = get_setting("city", DEFAULT_CITY)
    return code if code in CITIES else DEFAULT_CITY


def set_city(code: str):
    if code in CITIES:
        set_setting("city", code)

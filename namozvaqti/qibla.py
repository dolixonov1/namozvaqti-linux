import math

# Kaaba, Masjid al-Haram
KAABA_LAT = 21.4225
KAABA_LNG = 39.8262


def qibla_direction(lat: float, lng: float) -> float:
    """Great-circle initial bearing (degrees from true north) toward the Kaaba.

    Computed locally so it works offline — same spherical formula Aladhan's
    /qibla endpoint uses, no network call needed.
    """
    phi1 = math.radians(lat)
    phi2 = math.radians(KAABA_LAT)
    dlng = math.radians(KAABA_LNG - lng)

    x = math.sin(dlng) * math.cos(phi2)
    y = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(dlng)

    return (math.degrees(math.atan2(x, y)) + 360) % 360

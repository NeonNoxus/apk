"""
weather.py
----------
Original nutzte vermutlich einen bezahlpflichtigen Wetterdienst. Für die
Android-Version verwenden wir Open-Meteo, weil es keinen API-Key braucht
(wichtig, damit die App sofort ohne Zusatz-Setup läuft) und weltweit
funktioniert.
"""

import requests

TOOL = {
    "name": "get_weather",
    "description": "Ruft das aktuelle Wetter und die Vorhersage für einen Ort ab.",
    "parameters": {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "Stadtname, z.B. 'Berlin' oder 'München'"},
        },
        "required": ["city"],
    },
}


def _geocode(city):
    r = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1, "language": "de"},
        timeout=10,
    )
    r.raise_for_status()
    results = r.json().get("results")
    if not results:
        return None
    top = results[0]
    return top["latitude"], top["longitude"], top.get("name", city)


def run(city):
    geo = _geocode(city)
    if not geo:
        return f"Konnte den Ort '{city}' nicht finden."
    lat, lon, resolved_name = geo

    r = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",
            "daily": "temperature_2m_max,temperature_2m_min",
            "timezone": "auto",
        },
        timeout=10,
    )
    r.raise_for_status()
    data = r.json()
    current = data["current"]
    daily = data["daily"]

    return (
        f"Wetter in {resolved_name}: aktuell {current['temperature_2m']}°C, "
        f"Luftfeuchtigkeit {current['relative_humidity_2m']}%, "
        f"Wind {current['wind_speed_10m']} km/h. "
        f"Heute: {daily['temperature_2m_min'][0]}°C bis {daily['temperature_2m_max'][0]}°C."
    )

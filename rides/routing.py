import json
import math
from decimal import Decimal, ROUND_HALF_UP, ROUND_CEILING
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError, HTTPError

from django.conf import settings


def calculate_route_metrics(
    pickup_latitude,
    pickup_longitude,
    destination_latitude,
    destination_longitude,
):
    token = settings.MAPBOX_ACCESS_TOKEN

    if not token:
        raise ValueError("Mapbox token sozlanmagan.")

    coordinates = (
        f"{pickup_longitude},{pickup_latitude};"
        f"{destination_longitude},{destination_latitude}"
    )

    params = urlencode({
        "access_token": token,
        "overview": "false",
        "steps": "false",
    })

    url = (
        "https://api.mapbox.com/directions/v5/"
        f"mapbox/driving-traffic/{coordinates}?{params}"
    )

    try:
        with urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))

    except (HTTPError, URLError, TimeoutError) as error:
        raise ValueError("Mapbox xizmatiga ulanib bo'lmadi.") from error

    routes = data.get("routes", [])

    if data.get("code") != "Ok" or not routes:
        raise ValueError("Ushbu manzillar orasida marshrut topilmadi.")

    route = routes[0]

    distance_km = (
        Decimal(str(route["distance"])) / Decimal("1000")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    duration_minutes = (
        Decimal(str(route["duration"])) / Decimal("60")
    ).quantize(Decimal("1"), rounding=ROUND_CEILING)

    return distance_km, duration_minutes
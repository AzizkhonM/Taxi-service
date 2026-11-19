from decimal import Decimal, ROUND_HALF_UP

BASE_FARE = Decimal("5000")
PRICE_PER_KM = Decimal("2000")
PRICE_PER_MINUTE = Decimal("200")


def calculate_fare(distance_km, duration_minutes):
    distance = Decimal(str(distance_km))
    duration = Decimal(str(duration_minutes))

    total = (
        BASE_FARE
        + (distance * PRICE_PER_KM)
        + (duration * PRICE_PER_MINUTE)
    )

    return int(total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
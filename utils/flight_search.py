
from datetime import datetime, date, time, timedelta
from decimal import Decimal
import hashlib

from sqlalchemy import select

from database.connection import SessionLocal
from database.models import Airport


# --------------------------------------------------
# AIRPORT SEARCH
# --------------------------------------------------

def get_airports(search_text: str = ""):
    db = SessionLocal()

    try:
        query = select(Airport).where(
            Airport.is_active.is_(True)
        )

        if search_text.strip():
            term = f"%{search_text.strip()}%"

            query = query.where(
                (Airport.city.ilike(term))
                | (Airport.country.ilike(term))
                | (Airport.name.ilike(term))
                | (Airport.iata_code.ilike(term))
            )

        return db.scalars(
            query.order_by(Airport.city).limit(100)
        ).all()

    finally:
        db.close()


def get_airport_labels():
    airports = get_airports()

    return {
        f"{airport.city}, {airport.country} "
        f"— {airport.name} ({airport.iata_code})": airport.iata_code
        for airport in airports
    }


# --------------------------------------------------
# DEMO AIRLINES
# --------------------------------------------------

AIRLINES = [
    {
        "code": "AI",
        "name": "Air India",
        "base_price": 6200,
    },
    {
        "code": "6E",
        "name": "IndiGo",
        "base_price": 4800,
    },
    {
        "code": "UK",
        "name": "Vistara (sample branding)",
        "base_price": 6800,
    },
    {
        "code": "EK",
        "name": "Emirates",
        "base_price": 14500,
    },
    {
        "code": "QR",
        "name": "Qatar Airways",
        "base_price": 13500,
    },
    {
        "code": "SQ",
        "name": "Singapore Airlines",
        "base_price": 15500,
    },
]


# --------------------------------------------------
# DEMO OFFER GENERATOR
# --------------------------------------------------

def _stable_number(value: str, modulo: int) -> int:
    digest = hashlib.sha256(value.encode()).hexdigest()
    return int(digest[:12], 16) % modulo


def generate_demo_flights(
    origin_code: str,
    destination_code: str,
    departure_date: date,
    cabin_class: str,
    adults: int,
    children: int,
    infants: int,
    trip_type: str = "One-way",
):
    if origin_code == destination_code:
        return []

    offers = []

    passenger_count = adults + children + infants

    cabin_multipliers = {
        "Economy": 1.0,
        "Premium Economy": 1.55,
        "Business": 3.2,
        "First Class": 5.5,
    }

    multiplier = cabin_multipliers[cabin_class]

    route = f"{origin_code}-{destination_code}"

    for index, airline in enumerate(AIRLINES):

        seed = f"{route}-{departure_date}-{airline['code']}"

        departure_hour = 5 + _stable_number(seed + "hour", 14)
        departure_minute = _stable_number(seed + "minute", 4) * 15

        duration = 80 + _stable_number(seed + "duration", 720)

        stops = _stable_number(seed + "stops", 3)

        departure_datetime = datetime.combine(
            departure_date,
            time(departure_hour, departure_minute)
        )

        arrival_datetime = departure_datetime + timedelta(
            minutes=duration
        )

        route_factor = 1.0 + (
            _stable_number(route, 100) / 100
        )

        base_price = Decimal(str(airline["base_price"]))

        total_price = (
            base_price
            * Decimal(str(route_factor))
            * Decimal(str(multiplier))
            * Decimal(passenger_count)
        ).quantize(Decimal("1"))

        offers.append({
            "id": f"DEMO-{seed[:16]}",
            "provider": "DEMO",
            "airline_code": airline["code"],
            "airline_name": airline["name"],
            "flight_number": (
                f"{airline['code']}{100 + index * 23 + _stable_number(seed, 80)}"
            ),
            "origin_code": origin_code,
            "destination_code": destination_code,
            "departure": departure_datetime,
            "arrival": arrival_datetime,
            "duration_minutes": duration,
            "stops": stops,
            "cabin_class": cabin_class,
            "price": total_price,
            "currency": "INR",
            "trip_type": trip_type,
            "passengers": passenger_count,
            "is_demo": True,
        })

    return offers


# --------------------------------------------------
# FORMATTING
# --------------------------------------------------

def format_duration(minutes: int) -> str:
    hours = minutes // 60
    remaining_minutes = minutes % 60

    return f"{hours}h {remaining_minutes}m"


def format_price(amount: Decimal, currency: str = "INR") -> str:
    if currency == "INR":
        return f"₹{amount:,.0f}"

    return f"{currency} {amount:,.2f}"

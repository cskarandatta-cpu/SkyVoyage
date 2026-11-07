
from sqlalchemy import select

from database.connection import SessionLocal
from database.models import Airport


AIRPORTS = [
    ("DEL", "Indira Gandhi International Airport", "Delhi", "India", "Asia/Kolkata"),
    ("BOM", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai", "India", "Asia/Kolkata"),
    ("BLR", "Kempegowda International Airport", "Bengaluru", "India", "Asia/Kolkata"),
    ("HYD", "Rajiv Gandhi International Airport", "Hyderabad", "India", "Asia/Kolkata"),
    ("MAA", "Chennai International Airport", "Chennai", "India", "Asia/Kolkata"),
    ("CCU", "Netaji Subhas Chandra Bose International Airport", "Kolkata", "India", "Asia/Kolkata"),
    ("GOI", "Manohar International Airport", "Goa", "India", "Asia/Kolkata"),
    ("AMD", "Sardar Vallabhbhai Patel International Airport", "Ahmedabad", "India", "Asia/Kolkata"),
    ("COK", "Cochin International Airport", "Kochi", "India", "Asia/Kolkata"),
    ("DXB", "Dubai International Airport", "Dubai", "United Arab Emirates", "Asia/Dubai"),
    ("DOH", "Hamad International Airport", "Doha", "Qatar", "Asia/Qatar"),
    ("SIN", "Singapore Changi Airport", "Singapore", "Singapore", "Asia/Singapore"),
    ("LHR", "Heathrow Airport", "London", "United Kingdom", "Europe/London"),
    ("JFK", "John F. Kennedy International Airport", "New York", "United States", "America/New_York"),
    ("CDG", "Charles de Gaulle Airport", "Paris", "France", "Europe/Paris"),
    ("HND", "Haneda Airport", "Tokyo", "Japan", "Asia/Tokyo"),
    ("BKK", "Suvarnabhumi Airport", "Bangkok", "Thailand", "Asia/Bangkok"),
    ("KUL", "Kuala Lumpur International Airport", "Kuala Lumpur", "Malaysia", "Asia/Kuala_Lumpur"),
    ("AUH", "Zayed International Airport", "Abu Dhabi", "United Arab Emirates", "Asia/Dubai"),
]


def seed_airports():
    db = SessionLocal()

    try:
        added = 0

        for code, name, city, country, timezone in AIRPORTS:

            existing = db.scalar(
                select(Airport).where(Airport.iata_code == code)
            )

            if existing:
                continue

            airport = Airport(
                iata_code=code,
                name=name,
                city=city,
                country=country,
                timezone=timezone,
                is_active=True,
            )

            db.add(airport)
            added += 1

        db.commit()

        print(f"Airport seeding successful. Added {added} airports.")
        print(f"Total airports in starter dataset: {len(AIRPORTS)}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_airports()

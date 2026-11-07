from sqlalchemy.orm import configure_mappers

from database.models import (
    User,
    Airport,
    FlightOffer,
    Booking,
    Passenger,
    SeatSelection,
    Payment,
    Wishlist,
    RecentSearch,
)

configure_mappers()

print("SUCCESS: All SQLAlchemy relationships configured correctly.")
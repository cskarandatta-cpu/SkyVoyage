
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


def utc_now():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    full_name: Mapped[str] = mapped_column(String(150), nullable=False)

    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    password_hash: Mapped[str | None] = mapped_column(String(255))

    phone: Mapped[str | None] = mapped_column(String(30))

    google_id: Mapped[str | None] = mapped_column(
        String(255), unique=True
    )

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Role-based access: user or admin
    role: Mapped[str] = mapped_column(
        String(20), default="user", nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    bookings = relationship("Booking", back_populates="user")
    wishlist = relationship("Wishlist", back_populates="user")
class Airport(Base):
    __tablename__ = "airports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    iata_code: Mapped[str] = mapped_column(
        String(3), unique=True, index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    timezone: Mapped[str | None] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class FlightOffer(Base):
    __tablename__ = "flight_offers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_offer_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )

    airline_code: Mapped[str] = mapped_column(String(5), nullable=False)
    airline_name: Mapped[str] = mapped_column(String(150))
    flight_number: Mapped[str] = mapped_column(String(30))

    origin_code: Mapped[str] = mapped_column(
        ForeignKey("airports.iata_code"), nullable=False
    )
    destination_code: Mapped[str] = mapped_column(
        ForeignKey("airports.iata_code"), nullable=False
    )

    departure_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    arrival_time: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    stops: Mapped[int] = mapped_column(Integer, default=0)

    cabin_class: Mapped[str] = mapped_column(
        String(30), default="Economy"
    )

    price_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )
    currency: Mapped[str] = mapped_column(String(3), default="INR")

    baggage_info: Mapped[dict | None] = mapped_column(JSON)
    raw_offer: Mapped[dict | None] = mapped_column(JSON)

    searched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )
    expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    bookings = relationship("Booking", back_populates="flight_offer")

    __table_args__ = (
        UniqueConstraint(
            "provider",
            "provider_offer_id",
            name="uq_provider_offer",
        ),
    )


class Booking(Base):
    __tablename__ = "bookings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    booking_reference: Mapped[str] = mapped_column(
        String(20), unique=True, index=True, nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    flight_offer_id: Mapped[int | None] = mapped_column(
        ForeignKey("flight_offers.id", ondelete="SET NULL")
    )

    status: Mapped[str] = mapped_column(
        String(30), default="pending_payment"
    )

    payment_status: Mapped[str] = mapped_column(
        String(30), default="pending"
    )

    total_amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    currency: Mapped[str] = mapped_column(String(3), default="INR")

    # Flight details snapshot, retained even if an offer expires.
    flight_snapshot: Mapped[dict | None] = mapped_column(JSON)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    confirmed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )
    cancelled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    cancellation_reason: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )

    refund_status: Mapped[str] = mapped_column(
        String(30), default="not_applicable_demo"
    )

    user = relationship("User", back_populates="bookings")
    flight_offer = relationship(
        "FlightOffer", back_populates="bookings"
    )

    passengers = relationship(
        "Passenger", back_populates="booking",
        cascade="all, delete-orphan"
    )

    payments = relationship(
        "Payment", back_populates="booking",
        cascade="all, delete-orphan"
    )

    seats = relationship(
        "SeatSelection", back_populates="booking",
        cascade="all, delete-orphan"
    )



class Passenger(Base):
    __tablename__ = "passengers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id"), nullable=False
    )

    full_name: Mapped[str] = mapped_column(
        String(150), nullable=False
    )

    date_of_birth: Mapped[datetime | None] = mapped_column(DateTime)
    gender: Mapped[str | None] = mapped_column(String(20))

    email: Mapped[str | None] = mapped_column(String(255))
    phone: Mapped[str | None] = mapped_column(String(30))

    baggage_option: Mapped[str] = mapped_column(
        String(50), default="Standard"
    )

    baggage_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=Decimal("0.00")
    )

    meal_preference: Mapped[str] = mapped_column(
        String(50), default="No preference"
    )

    # Store encrypted passport data, never plaintext.
    passport_number_encrypted: Mapped[str | None] = mapped_column(Text)
    passport_expiry: Mapped[datetime | None] = mapped_column(DateTime)
    passport_country: Mapped[str | None] = mapped_column(String(100))

    passenger_type: Mapped[str] = mapped_column(
        String(20), default="adult"
    )

    booking = relationship("Booking", back_populates="passengers")

    seat = relationship(
        "SeatSelection",
        back_populates="passenger",
        uselist=False
    )



class SeatSelection(Base):
    __tablename__ = "seat_selections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id"), nullable=False
    )

    passenger_id: Mapped[int] = mapped_column(
        ForeignKey("passengers.id"), unique=True, nullable=False
    )

    seat_number: Mapped[str] = mapped_column(String(10), nullable=False)
    cabin_class: Mapped[str] = mapped_column(String(30))
    additional_price: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00")
    )

    booking = relationship("Booking", back_populates="seats")
    passenger = relationship("Passenger", back_populates="seat")


class Payment(Base):
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    booking_id: Mapped[int] = mapped_column(
        ForeignKey("bookings.id"), nullable=False
    )

    gateway: Mapped[str] = mapped_column(String(30), nullable=False)
    payment_method: Mapped[str | None] = mapped_column(
    String(30), nullable=True
)

    gateway_order_id: Mapped[str | None] = mapped_column(
        String(255), unique=True
    )

    gateway_payment_id: Mapped[str | None] = mapped_column(
        String(255), unique=True
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), nullable=False
    )

    currency: Mapped[str] = mapped_column(String(3), default="INR")

    status: Mapped[str] = mapped_column(
        String(30), default="created"
    )

    signature_verified: Mapped[bool] = mapped_column(
        Boolean, default=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    booking = relationship("Booking", back_populates="payments")


class Wishlist(Base):
    __tablename__ = "wishlist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )

    origin_code: Mapped[str] = mapped_column(
        String(3), nullable=False
    )

    destination_code: Mapped[str] = mapped_column(
        String(3), nullable=False
    )

    # Complete saved demo flight details.
    flight_snapshot: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )

    user = relationship("User", back_populates="wishlist")



class RecentSearch(Base):
    __tablename__ = "recent_searches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE")
    )

    origin_code: Mapped[str] = mapped_column(String(3), nullable=False)
    destination_code: Mapped[str] = mapped_column(String(3), nullable=False)

    departure_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    return_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    passengers: Mapped[int] = mapped_column(Integer, default=1)
    adults: Mapped[int] = mapped_column(Integer, default=1)
    children: Mapped[int] = mapped_column(Integer, default=0)
    infants: Mapped[int] = mapped_column(Integer, default=0)

    cabin_class: Mapped[str] = mapped_column(
        String(30), default="Economy"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now
    )


import streamlit as st

from html import escape

from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal
from database.models import Booking


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Booking Details | SkyVoyage",
    page_icon="✈️",
    layout="wide",
)


# --------------------------------------------------
# PREMIUM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 5% 0%,
                rgba(56, 130, 246, 0.09),
                transparent 30%
            ),
            linear-gradient(135deg, #f7f9ff, #eef3ff);
    }

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .details-hero {
        background: linear-gradient(
            120deg,
            #101d45,
            #245ca8,
            #7355b7
        );
        padding: 35px;
        border-radius: 23px;
        color: white;
        margin-bottom: 25px;
        box-shadow: 0 12px 35px rgba(25, 55, 110, 0.16);
    }

    .details-hero h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .details-hero p {
        color: #e5edff;
        margin-bottom: 0;
    }

    .section-heading {
        color: #173b70;
        font-size: 1.4rem;
        font-weight: 800;
        margin-top: 12px;
        margin-bottom: 15px;
    }

    .info-card {
        background: white;
        border: 1px solid #e1e9f5;
        border-radius: 18px;
        padding: 21px;
        box-shadow: 0 5px 18px rgba(20, 50, 100, 0.05);
        margin-bottom: 13px;
    }

    .info-label {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 5px;
    }

    .info-value {
        color: #173b70;
        font-size: 1.08rem;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .route-display {
        background: linear-gradient(135deg, #eef4ff, #f5f0ff);
        border: 1px solid #dce6f5;
        border-radius: 18px;
        padding: 25px;
        text-align: center;
        margin-bottom: 18px;
    }

    .route-codes {
        color: #173b70;
        font-size: 2rem;
        font-weight: 800;
    }

    .route-subtitle {
        color: #64748b;
        font-size: 0.9rem;
        margin-top: 7px;
    }

    .status-confirmed {
        background: #dcfce7;
        color: #166534;
        padding: 7px 13px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 800;
        display: inline-block;
    }

    .status-pending {
        background: #fef3c7;
        color: #92400e;
        padding: 7px 13px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 800;
        display: inline-block;
    }

    .status-cancelled {
        background: #fee2e2;
        color: #991b1b;
        padding: 7px 13px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 800;
        display: inline-block;
    }

    .status-other {
        background: #e2e8f0;
        color: #475569;
        padding: 7px 13px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 800;
        display: inline-block;
    }

    .cancel-notice {
        background: #fff7e8;
        border: 1px solid #f3d29a;
        color: #854d0e;
        padding: 19px;
        border-radius: 15px;
        margin-bottom: 18px;
    }

    .total-card {
        background: linear-gradient(120deg, #101d45, #245ca8);
        color: white;
        padding: 25px;
        border-radius: 19px;
        text-align: center;
        margin-top: 12px;
    }

    .total-card .label {
        color: #dbeafe;
        font-size: 0.85rem;
        font-weight: 600;
    }

    .total-card .amount {
        color: white;
        font-size: 2rem;
        font-weight: 800;
        margin-top: 5px;
    }

    div.stButton > button {
        border-radius: 11px;
        font-weight: 700;
        min-height: 45px;
    }

    @media (max-width: 768px) {
        .details-hero {
            padding: 25px 18px;
        }

        .details-hero h1 {
            font-size: 1.8rem;
        }

        .route-codes {
            font-size: 1.6rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def flight_value(snapshot, *keys, default="—"):
    """Return the first available flight snapshot value."""

    for key in keys:
        value = snapshot.get(key)

        if value is not None and value != "":
            return str(value)

    return default


def status_information(status):
    """Return a readable booking status and CSS class."""

    if status == "demo_confirmed":
        return "✓ Demo Confirmed", "status-confirmed"

    if status == "demo_pending":
        return "◷ Payment Pending", "status-pending"

    if status == "demo_cancelled":
        return "✕ Demo Cancelled", "status-cancelled"

    return (
        str(status).replace("_", " ").title(),
        "status-other",
    )


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

user_id = st.session_state.get("user_id")
booking_id = st.session_state.get("selected_booking_id")

if user_id is None:
    st.warning("Please log in first.")
    st.page_link("app.py", label="Go to Login")
    st.stop()

if booking_id is None:
    st.warning("No booking selected.")
    st.page_link(
        "pages/6_My_Trips.py",
        label="Go to My Trips",
    )
    st.stop()


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="details-hero">
        <h1>📋 Booking Details</h1>
        <p>
            Your complete itinerary, passengers,
            payment history and booking information.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# LOAD SELECTED BOOKING
# --------------------------------------------------

db = SessionLocal()

try:

    booking = (
        db.query(Booking)
        .options(
            selectinload(Booking.passengers),
            selectinload(Booking.seats),
            selectinload(Booking.payments),
        )
        .filter(
            Booking.id == booking_id,
            Booking.user_id == user_id,
        )
        .first()
    )

    if not booking:
        st.error("Booking not found or access denied.")
        st.stop()

    snapshot = booking.flight_snapshot or {}

    origin = flight_value(snapshot, "origin_code", "origin")
    destination = flight_value(
        snapshot,
        "destination_code",
        "destination",
    )

    airline = flight_value(
        snapshot,
        "airline_name",
        "airline",
        default="Demo Airline",
    )

    flight_number = flight_value(
        snapshot,
        "flight_number",
    )

    departure = flight_value(
        snapshot,
        "departure_time",
        "departure",
    )

    arrival = flight_value(
        snapshot,
        "arrival_time",
        "arrival",
    )

    cabin = flight_value(
        snapshot,
        "cabin_class",
        "cabin",
        default="Economy",
    )

    provider = flight_value(
        snapshot,
        "provider",
        default="DEMO",
    )

    status_label, status_class = status_information(
        booking.status
    )

    currency = booking.currency or "INR"
    total_amount = float(booking.total_amount or 0)

    # Map seat selections to passengers

    seats_by_passenger = {
        seat.passenger_id: seat
        for seat in booking.seats
    }

    # --------------------------------------------------
    # BOOKING OVERVIEW
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">Booking Overview</div>',
        unsafe_allow_html=True,
    )

    overview1, overview2, overview3 = st.columns(3)

    with overview1:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Booking Reference</div>
                <div class="info-value">
                    {escape(str(booking.booking_reference))}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with overview2:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Booking Status</div>
                <div style="margin-top:8px;">
                    <span class="{status_class}">
                        {escape(status_label)}
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with overview3:
        payment_status = str(
            booking.payment_status or "Unknown"
        ).replace("_", " ").title()

        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Payment Status</div>
                <div class="info-value">
                    {escape(payment_status)}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # --------------------------------------------------
    # CANCELLATION INFORMATION
    # --------------------------------------------------

    if booking.status == "demo_cancelled":

        st.markdown(
            """
            <div class="section-heading">
                Cancellation Information
            </div>
            """,
            unsafe_allow_html=True,
        )

        cancellation_date = (
            booking.cancelled_at.strftime(
                "%d %B %Y, %I:%M %p UTC"
            )
            if booking.cancelled_at
            else "Not available"
        )

        cancellation_reason = (
            booking.cancellation_reason or "Not provided"
        )

        refund_status = str(
            booking.refund_status or "Not available"
        ).replace("_", " ").title()

        st.markdown(
            f"""
            <div class="cancel-notice">
                <h3>❌ Demo Booking Cancelled</h3>
                <p>
                    <b>Cancellation date:</b>
                    {escape(cancellation_date)}
                </p>
                <p>
                    <b>Cancellation reason:</b>
                    {escape(cancellation_reason)}
                </p>
                <p>
                    <b>Refund status:</b>
                    {escape(refund_status)}
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if booking.refund_status == "simulated_refunded":

            st.success(
                "Your demo refund has been marked as simulated refunded."
            )

            st.info(
                "This is only a demonstration. No real payment "
                "was collected and no actual money was refunded."
            )

        else:

            st.info(
                "No refund is applicable to this demo booking."
            )

    st.divider()

    # --------------------------------------------------
    # FLIGHT ITINERARY
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">✈️ Flight Itinerary</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="route-display">
            <div class="route-codes">
                {escape(origin)} → {escape(destination)}
            </div>
            <div class="route-subtitle">
                {escape(airline)} · {escape(flight_number)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    flight_col1, flight_col2 = st.columns(2)

    with flight_col1:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Departure Airport</div>
                <div class="info-value">{escape(origin)}</div>
                <br>
                <div class="info-label">Departure Time</div>
                <div class="info-value">{escape(departure)}</div>
                <br>
                <div class="info-label">Airline</div>
                <div class="info-value">{escape(airline)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with flight_col2:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Arrival Airport</div>
                <div class="info-value">{escape(destination)}</div>
                <br>
                <div class="info-label">Arrival Time</div>
                <div class="info-value">{escape(arrival)}</div>
                <br>
                <div class="info-label">Flight Number</div>
                <div class="info-value">{escape(flight_number)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    extra_col1, extra_col2 = st.columns(2)

    with extra_col1:
        st.write("**Cabin class:**", cabin)

    with extra_col2:
        st.write("**Provider:**", provider)

    st.divider()

    # --------------------------------------------------
    # PASSENGER DETAILS
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">👥 Passenger Information</div>',
        unsafe_allow_html=True,
    )

    if booking.passengers:

        for index, passenger in enumerate(
            booking.passengers,
            start=1,
        ):

            seat = seats_by_passenger.get(passenger.id)

            seat_number = (
                seat.seat_number
                if seat
                else "Not selected"
            )

            seat_charge = (
                float(seat.additional_price or 0)
                if seat
                else 0
            )

            with st.expander(
                f"Passenger {index}: {passenger.full_name}",
                expanded=True,
            ):

                passenger_col1, passenger_col2 = st.columns(2)

                with passenger_col1:
                    st.write("**Name:**", passenger.full_name)

                    st.write(
                        "**Passenger type:**",
                        getattr(
                            passenger,
                            "passenger_type",
                            "adult",
                        ),
                    )

                    st.write(
                        "**Email:**",
                        passenger.email or "—",
                    )

                    st.write(
                        "**Phone:**",
                        passenger.phone or "—",
                    )

                with passenger_col2:
                    st.write(
                        "**Selected seat:**",
                        seat_number,
                    )

                    st.write(
                        "**Seat charge:**",
                        f"{currency} {seat_charge:,.2f}",
                    )

                    st.write(
                        "**Baggage:**",
                        passenger.baggage_option or "Standard",
                    )

                    st.write(
                        "**Meal preference:**",
                        passenger.meal_preference or "No preference",
                    )

    else:
        st.info("No passenger records are available.")

    st.divider()

    # --------------------------------------------------
    # PAYMENT HISTORY
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">💳 Payment History</div>',
        unsafe_allow_html=True,
    )

    if booking.payments:

        sorted_payments = sorted(
            booking.payments,
            key=lambda item: item.id,
            reverse=True,
        )

        for payment in sorted_payments:

            payment_label = str(
                payment.status
            ).replace("_", " ").title()

            with st.expander(
                f"Payment #{payment.id} — {payment_label}",
                expanded=True,
            ):

                pay_col1, pay_col2 = st.columns(2)

                with pay_col1:
                    st.write(
                        "**Gateway:**",
                        payment.gateway or "—",
                    )

                    st.write(
                        "**Payment method:**",
                        payment.payment_method or "—",
                    )

                    st.write(
                        "**Transaction reference:**",
                        (
                            payment.gateway_payment_id
                            or payment.gateway_order_id
                            or "—"
                        ),
                    )

                with pay_col2:
                    payment_currency = (
                        payment.currency or currency
                    )

                    st.write(
                        "**Amount:**",
                        f"{payment_currency} "
                        f"{float(payment.amount or 0):,.2f}",
                    )

                    st.write(
                        "**Payment status:**",
                        payment_label,
                    )

                    st.write(
                        "**Payment ID:**",
                        payment.id,
                    )

    else:
        st.info("No payment records are available.")

    st.divider()

    # --------------------------------------------------
    # BOOKING TOTAL
    # --------------------------------------------------

    st.markdown(
        f"""
        <div class="total-card">
            <div class="label">Total Booking Amount</div>
            <div class="amount">
                {escape(str(currency))} {total_amount:,.2f}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="cancel-notice">
            <b>Demo booking notice:</b><br>
            This is not a valid airline ticket.
            No real airline reservation or payment was created.
            Any cancellation or refund shown here is simulated.
        </div>
        """,
        unsafe_allow_html=True,
    )

except SQLAlchemyError:
    st.error(
        "Unable to load booking details. Please try again."
    )

finally:
    db.close()


# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

st.divider()

nav_col1, nav_col2 = st.columns(2)

with nav_col1:
    if st.button(
        "← Back to My Trips",
        use_container_width=True,
    ):
        st.switch_page("pages/6_My_Trips.py")

with nav_col2:
    if st.button(
        "🏠 Back to Home",
        use_container_width=True,
    ):
        st.switch_page("app.py")

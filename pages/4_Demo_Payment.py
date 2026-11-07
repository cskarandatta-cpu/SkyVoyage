
import secrets
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation

import streamlit as st
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal
from database.models import Booking, Payment


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Secure Checkout | SkyVoyage",
    page_icon="💳",
    layout="wide",
)


# --------------------------------------------------
# PREMIUM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 5% 5%, rgba(76,130,255,.10), transparent 28%),
            radial-gradient(circle at 95% 15%, rgba(145,100,255,.09), transparent 25%),
            var(--background-color);
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -.6px;
    }

    .sv-hero {
        padding: 30px 32px;
        border-radius: 22px;
        margin-bottom: 24px;
        color: white;
        background: linear-gradient(120deg, #101d40, #174a83 55%, #5367c9);
        box-shadow: 0 12px 35px rgba(20,50,100,.18);
    }

    .sv-hero h1 {
        color: white !important;
        font-size: clamp(28px, 4vw, 42px);
        font-weight: 800;
        margin: 0;
    }

    .sv-hero p {
        color: #e1ebff;
        margin: 10px 0 0 0;
    }

    .sv-eyebrow {
        color: #b8d8ff;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        margin-bottom: 9px;
    }

    .sv-label {
        color: #568ce8;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .sv-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(120,150,200,.22);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 14px;
        box-shadow: 0 5px 20px rgba(30,60,110,.05);
    }

    .sv-route {
        font-size: 27px;
        font-weight: 800;
        color: #4c83e6;
    }

    .sv-price {
        font-size: 32px;
        font-weight: 800;
        color: #4c83e6;
    }

    .sv-muted {
        color: #8292aa;
        font-size: 13px;
    }

    .sv-demo {
        padding: 16px;
        border-radius: 13px;
        background: rgba(245,180,50,.10);
        border: 1px solid rgba(245,180,50,.35);
        margin: 14px 0;
    }

    .sv-step {
        background: var(--secondary-background-color);
        border: 1px solid rgba(120,150,200,.2);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 22px;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 11px;
        min-height: 45px;
        font-weight: 700;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(100deg, #2877df, #6559d9);
        border: none;
        color: white;
    }

    @media(max-width:768px) {
        .sv-hero {
            padding: 23px 20px;
        }

        .sv-card {
            padding: 15px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HERO
# --------------------------------------------------

st.markdown(
    """
    <div class="sv-hero">
        <div class="sv-eyebrow">SKYVOYAGE · CHECKOUT</div>
        <h1>Secure Checkout</h1>
        <p>Review your journey and complete your demo payment.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sv-step">
        <strong>01 · Flight</strong>
        &nbsp; → &nbsp;
        <strong>02 · Passengers</strong>
        &nbsp; → &nbsp;
        <strong>03 · Seats & extras</strong>
        &nbsp; → &nbsp;
        <strong>04 · Payment</strong>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sv-demo">
        <strong>DEMO PAYMENT MODE</strong><br>
        This is a simulated transaction. No real money will be collected.
        Never enter actual card numbers, UPI IDs or banking credentials.
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# AUTHENTICATION AND BOOKING
# --------------------------------------------------

user_id = st.session_state.get("user_id")
created_booking = st.session_state.get("created_booking")

if user_id is None:
    st.warning("Please log in before making a payment.")
    st.page_link("app.py", label="Go to Login")
    st.stop()

if not created_booking or not created_booking.get("id"):
    st.error("No booking was found. Please select a flight first.")
    st.page_link(
        "pages/1_Search_Flights.py",
        label="Back to Flight Search",
    )
    st.stop()

try:
    booking_id = int(created_booking["id"])
except (ValueError, TypeError):
    st.error("Invalid booking information. Please start again.")
    st.stop()


# --------------------------------------------------
# ERROR FEEDBACK
# --------------------------------------------------

if st.session_state.get("demo_payment_error"):
    st.error(st.session_state.demo_payment_error)
    st.session_state.pop("demo_payment_error", None)


# --------------------------------------------------
# DATABASE LOOKUP
# --------------------------------------------------

db = SessionLocal()

try:

    booking = db.execute(
        select(Booking)
        .options(
            selectinload(Booking.passengers),
            selectinload(Booking.seats),
            selectinload(Booking.payments),
        )
        .where(
            Booking.id == booking_id,
            Booking.user_id == user_id,
        )
    ).scalar_one_or_none()

    if not booking:
        st.error("Booking not found or access denied.")
        st.stop()

    if booking.status == "demo_confirmed":
        st.success("Your demo payment has already been completed.")

        st.markdown(
            f"**Booking reference:** `{booking.booking_reference}`"
        )

        if st.button(
            "View Booking Confirmation",
            type="primary",
            use_container_width=True,
        ):
            st.switch_page("pages/5_Booking_Confirmation.py")

        st.stop()

    if booking.status != "demo_pending":
        st.error(
            "This booking cannot be paid in its current status: "
            f"{booking.status}"
        )
        st.stop()

    try:
        amount = Decimal(str(booking.total_amount))

        if not amount.is_finite() or amount <= 0:
            raise ValueError

    except (InvalidOperation, ValueError):
        st.error("Invalid booking amount. Payment cannot continue.")
        st.stop()

    passengers = sorted(
        booking.passengers,
        key=lambda passenger: passenger.id,
    )

    flight = booking.flight_snapshot or {}


    # --------------------------------------------------
    # BOOKING SUMMARY
    # --------------------------------------------------

    st.markdown(
        '<div class="sv-label">YOUR BOOKING</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Review your journey")

    with st.container(border=True):

        col1, col2, col3 = st.columns([1, 1.4, 1])

        with col1:
            st.caption("AIRLINE")
            st.markdown(
                f"**{flight.get('airline_name', 'Demo Airline')}**"
            )
            st.caption(
                flight.get("flight_number", "DEMO")
            )

        with col2:
            st.caption("FLIGHT ROUTE")
            st.markdown(
                f'<div class="sv-route">'
                f'{flight.get("origin_code", "Origin")} → '
                f'{flight.get("destination_code", "Destination")}'
                f'</div>',
                unsafe_allow_html=True,
            )

        with col3:
            st.caption("BOOKING REFERENCE")
            st.code(booking.booking_reference)

        st.divider()

        departure_text = flight.get("departure", "")
        arrival_text = flight.get("arrival", "")

        col1, col2 = st.columns(2)

        with col1:
            st.caption("DEPARTURE")
            st.write(departure_text or "Not available")

        with col2:
            st.caption("ARRIVAL")
            st.write(arrival_text or "Not available")

        st.caption(
            f"Cabin class: {flight.get('cabin_class', 'Economy')}"
        )


    # --------------------------------------------------
    # PASSENGER AND EXTRA DETAILS
    # --------------------------------------------------

    st.markdown(
        '<div class="sv-label">TRAVELLERS & EXTRAS</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Passenger details")

    for index, passenger in enumerate(passengers):

        seat = next(
            (
                item for item in booking.seats
                if item.passenger_id == passenger.id
            ),
            None,
        )

        with st.container(border=True):

            st.markdown(
                f"**Passenger {index + 1}: {passenger.full_name}**"
            )

            col1, col2 = st.columns(2)

            with col1:
                st.write(
                    f"Seat: {seat.seat_number if seat else 'Not selected'}"
                )
                st.write(
                    f"Baggage: {passenger.baggage_option or 'Standard'}"
                )

            with col2:
                st.write(
                    f"Meal: {passenger.meal_preference or 'No preference'}"
                )

                if passenger.email:
                    st.caption(passenger.email)


    # --------------------------------------------------
    # PRICE BREAKDOWN
    # --------------------------------------------------

    base_fare = Decimal(str(flight.get("price", "0")))

    seat_total = sum(
        (
            Decimal(str(item.additional_price or 0))
            for item in booking.seats
        ),
        Decimal("0.00"),
    )

    baggage_total = sum(
        (
            Decimal(str(passenger.baggage_price or 0))
            for passenger in passengers
        ),
        Decimal("0.00"),
    )

    st.markdown(
        '<div class="sv-label">PAYMENT SUMMARY</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Fare breakdown")

    with st.container(border=True):

        col1, col2 = st.columns(2)

        with col1:
            st.write("Base flight fare")

        with col2:
            st.write(f"₹{base_fare:,.2f}")

        col1, col2 = st.columns(2)

        with col1:
            st.write("Seat charges")

        with col2:
            st.write(f"₹{seat_total:,.2f}")

        col1, col2 = st.columns(2)

        with col1:
            st.write("Baggage charges")

        with col2:
            st.write(f"₹{baggage_total:,.2f}")

        st.divider()

        st.caption("TOTAL DEMO AMOUNT")

        st.markdown(
            f'<div class="sv-price">₹{amount:,.2f}</div>',
            unsafe_allow_html=True,
        )

        st.caption(f"Currency: {booking.currency}")


    # --------------------------------------------------
    # DEMO PAYMENT FORM
    # --------------------------------------------------

    st.markdown(
        '<div class="sv-label">PAYMENT METHOD</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Choose how to pay")

    st.caption(
        "Choose a simulated payment method. "
        "No actual payment provider is connected."
    )

    with st.form("demo_payment_form"):

        payment_method = st.radio(
            "Select payment method",
            options=[
                "UPI",
                "Credit / Debit Card",
                "Net Banking",
                "Wallet",
            ],
            horizontal=False,
        )

        st.divider()

        st.markdown("**Payment testing controls**")

        payment_outcome = st.radio(
            "Choose the simulated result",
            options=[
                "Simulate successful payment",
                "Simulate failed payment",
            ],
        )

        accepted = st.checkbox(
            "I understand that this is a simulated payment "
            "and no real money will be collected."
        )

        pay_button = st.form_submit_button(
            f"Pay ₹{amount:,.2f}",
            type="primary",
            use_container_width=True,
        )


    # --------------------------------------------------
    # PROCESS DEMO PAYMENT
    # --------------------------------------------------

    if pay_button:

        if not accepted:

            st.error(
                "Please acknowledge the demo payment notice."
            )

        else:

            try:

                # Lock the booking row to reduce concurrent payment attempts.
                locked_booking = db.execute(
                    select(Booking)
                    .where(
                        Booking.id == booking_id,
                        Booking.user_id == user_id,
                    )
                    .with_for_update()
                ).scalar_one_or_none()

                if not locked_booking:
                    raise ValueError("Booking could not be found.")

                if locked_booking.status != "demo_pending":
                    raise ValueError(
                        "This booking is no longer available for payment."
                    )

                # Recalculate amount from the latest database value.
                amount = Decimal(str(locked_booking.total_amount))

                transaction_code = secrets.token_hex(6).upper()

                is_success = (
                    payment_outcome == "Simulate successful payment"
                )

                payment = Payment(
                    booking_id=locked_booking.id,
                    gateway="demo",
                    payment_method=payment_method,
                    gateway_order_id=f"DEMO-ORDER-{transaction_code}",
                    gateway_payment_id=(
                        f"DEMO-PAY-{transaction_code}"
                        if is_success else None
                    ),
                    amount=amount,
                    currency=locked_booking.currency,
                    status=(
                        "success_demo"
                        if is_success
                        else "failed_demo"
                    ),
                    signature_verified=False,
                )

                db.add(payment)

                if is_success:

                    locked_booking.payment_status = "paid_demo"
                    locked_booking.status = "demo_confirmed"
                    locked_booking.confirmed_at = datetime.now(
                        timezone.utc
                    )

                else:

                    locked_booking.payment_status = "failed_demo"

                db.commit()

                if is_success:

                    st.session_state.created_booking = {
                        "id": locked_booking.id,
                        "reference": locked_booking.booking_reference,
                        "amount": str(locked_booking.total_amount),
                        "passenger_count": len(passengers),
                    }

                    st.session_state.demo_payment_success = True

                    st.switch_page(
                        "pages/5_Booking_Confirmation.py"
                    )

                else:

                    st.session_state.demo_payment_error = (
                        "The simulated payment failed. "
                        "Your booking is still available for another attempt."
                    )

                    st.rerun()

            except ValueError as exc:

                db.rollback()
                st.error(str(exc))

            except SQLAlchemyError:

                db.rollback()

                st.error(
                    "A database error occurred while processing "
                    "your demo payment. Please try again."
                )


    # --------------------------------------------------
    # BACK NAVIGATION
    # --------------------------------------------------

    st.divider()

    if st.button(
        "← Back to Seats & Extras",
        use_container_width=True,
    ):
        st.switch_page(
            "pages/3_Seat_Baggage_Meals.py"
        )


finally:
    db.close()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SkyVoyage · Demonstration checkout · "
    "No real money is collected and no airline ticket is issued."
)

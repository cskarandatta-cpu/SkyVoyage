
import streamlit as st

from datetime import datetime, timezone
from html import escape

from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal
from database.models import Booking


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="My Trips | SkyVoyage",
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
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .trips-hero {
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

    .trips-hero h1 {
        color: white;
        font-size: 2.3rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .trips-hero p {
        color: #e5edff;
        font-size: 1rem;
        margin-bottom: 0;
    }

    .section-heading {
        color: #173b70;
        font-size: 1.4rem;
        font-weight: 800;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .booking-card {
        background: white;
        border: 1px solid #e1e9f5;
        border-radius: 19px;
        padding: 21px;
        box-shadow: 0 5px 18px rgba(20, 50, 100, 0.05);
        margin-bottom: 13px;
    }

    .route {
        color: #173b70;
        font-size: 1.55rem;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .airline {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .booking-label {
        color: #64748b;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 4px;
    }

    .booking-value {
        color: #173b70;
        font-size: 1rem;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .booking-status {
        display: inline-block;
        padding: 7px 12px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .status-confirmed {
        color: #166534;
        background: #dcfce7;
    }

    .status-pending {
        color: #92400e;
        background: #fef3c7;
    }

    .status-cancelled {
        color: #991b1b;
        background: #fee2e2;
    }

    .status-other {
        color: #475569;
        background: #e2e8f0;
    }

    .cancel-notice {
        background: #fff7e8;
        border: 1px solid #f3d29a;
        color: #854d0e;
        padding: 15px;
        border-radius: 13px;
        margin-top: 13px;
        margin-bottom: 13px;
    }

    .empty-state {
        background: white;
        border: 1px solid #e1e9f5;
        border-radius: 20px;
        padding: 35px;
        text-align: center;
        color: #64748b;
    }

    div.stButton > button {
        border-radius: 11px;
        font-weight: 700;
        min-height: 43px;
    }

    @media (max-width: 768px) {
        .trips-hero {
            padding: 25px 18px;
        }

        .trips-hero h1 {
            font-size: 1.8rem;
        }

        .route {
            font-size: 1.3rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

user_id = st.session_state.get("user_id")

if user_id is None:
    st.warning("Please log in to view your trips.")
    st.page_link("app.py", label="Go to Login")
    st.stop()


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="trips-hero">
        <h1>✈️ My Trips</h1>
        <p>
            Your journeys, bookings and travel details,
            all in one place.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# CANCELLATION FUNCTION
# --------------------------------------------------

def cancel_demo_booking(
    booking_id: int,
    user_id: int,
    reason: str,
):
    db = SessionLocal()

    try:
        booking = (
            db.query(Booking)
            .filter(
                Booking.id == booking_id,
                Booking.user_id == user_id,
            )
            .with_for_update()
            .first()
        )

        if booking is None:
            return False, "Booking not found."

        if booking.status != "demo_confirmed":
            return False, "This booking cannot be cancelled."

        if booking.cancelled_at is not None:
            return False, "This booking has already been cancelled."

        booking.status = "demo_cancelled"
        booking.cancelled_at = datetime.now(timezone.utc)

        booking.cancellation_reason = (
            reason.strip() or "Cancelled by customer"
        )

        if booking.payment_status == "paid_demo":
            booking.payment_status = "refunded_demo"
            booking.refund_status = "simulated_refunded"
        else:
            booking.refund_status = "not_applicable_demo"

        db.commit()

        return True, "Demo booking cancelled successfully."

    except SQLAlchemyError:
        db.rollback()
        return False, (
            "Unable to cancel this booking. Please try again."
        )

    finally:
        db.close()


# --------------------------------------------------
# LOAD BOOKINGS
# --------------------------------------------------

db = SessionLocal()

try:
    bookings = (
        db.query(Booking)
        .options(
            selectinload(Booking.passengers),
            selectinload(Booking.seats),
            selectinload(Booking.payments),
        )
        .filter(Booking.user_id == user_id)
        .order_by(Booking.id.desc())
        .all()
    )

except SQLAlchemyError:
    st.error("Unable to load your bookings. Please try again.")
    bookings = []

finally:
    db.close()


# --------------------------------------------------
# EMPTY STATE
# --------------------------------------------------

if not bookings:
    st.markdown(
        """
        <div class="empty-state">
            <h2>✈️ No trips yet</h2>
            <p>
                Your next adventure is waiting.
                Search for a flight to get started.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "Search Flights",
        type="primary",
        use_container_width=True,
    ):
        st.switch_page("pages/1_Search_Flights.py")

    st.stop()


# --------------------------------------------------
# BOOKING STATISTICS
# --------------------------------------------------

total_bookings = len(bookings)

confirmed_bookings = sum(
    1 for booking in bookings
    if booking.status == "demo_confirmed"
)

pending_bookings = sum(
    1 for booking in bookings
    if booking.status == "demo_pending"
)

cancelled_bookings = sum(
    1 for booking in bookings
    if booking.status == "demo_cancelled"
)


st.markdown(
    '<div class="section-heading">Your Travel Overview</div>',
    unsafe_allow_html=True,
)

metric1, metric2, metric3, metric4 = st.columns(4)

with metric1:
    st.metric("Total Bookings", total_bookings)

with metric2:
    st.metric("Confirmed", confirmed_bookings)

with metric3:
    st.metric("Pending", pending_bookings)

with metric4:
    st.metric("Cancelled", cancelled_bookings)


st.divider()


# --------------------------------------------------
# BOOKING FILTERS
# --------------------------------------------------

st.markdown(
    '<div class="section-heading">Booking History</div>',
    unsafe_allow_html=True,
)

filter_col, info_col = st.columns([2, 3])

with filter_col:
    selected_filter = st.selectbox(
        "Filter your bookings",
        [
            "All bookings",
            "Confirmed",
            "Pending",
            "Cancelled",
            "Other",
        ],
        key="my_trips_filter",
    )

with info_col:
    st.caption(
        f"Showing your booking history · {len(bookings)} total bookings"
    )


if selected_filter == "Confirmed":
    visible_bookings = [
        booking for booking in bookings
        if booking.status == "demo_confirmed"
    ]

elif selected_filter == "Pending":
    visible_bookings = [
        booking for booking in bookings
        if booking.status == "demo_pending"
    ]

elif selected_filter == "Cancelled":
    visible_bookings = [
        booking for booking in bookings
        if booking.status == "demo_cancelled"
    ]

elif selected_filter == "Other":
    visible_bookings = [
        booking for booking in bookings
        if booking.status not in [
            "demo_confirmed",
            "demo_pending",
            "demo_cancelled",
        ]
    ]

else:
    visible_bookings = bookings


if not visible_bookings:
    st.info("No bookings match this filter.")


# --------------------------------------------------
# DISPLAY BOOKING CARDS
# --------------------------------------------------

for booking in visible_bookings:

    snapshot = booking.flight_snapshot or {}

    origin = snapshot.get("origin_code", "—")
    destination = snapshot.get("destination_code", "—")

    airline = snapshot.get(
        "airline_name",
        snapshot.get("airline", "Airline not available"),
    )

    flight_number = snapshot.get("flight_number", "—")

    departure = snapshot.get(
        "departure_time",
        snapshot.get("departure", "Not available"),
    )

    arrival = snapshot.get(
        "arrival_time",
        snapshot.get("arrival", "Not available"),
    )

    cabin = snapshot.get(
        "cabin_class",
        snapshot.get("cabin", "Not available"),
    )

    currency = booking.currency or "INR"
    amount = float(booking.total_amount or 0)
    passenger_count = len(booking.passengers)

    # Status styling

    if booking.status == "demo_confirmed":
        status_label = "✓ Demo Confirmed"
        status_class = "status-confirmed"

    elif booking.status == "demo_pending":
        status_label = "◷ Payment Pending"
        status_class = "status-pending"

    elif booking.status == "demo_cancelled":
        status_label = "✕ Demo Cancelled"
        status_class = "status-cancelled"

    else:
        status_label = str(booking.status).replace(
            "_", " "
        ).title()
        status_class = "status-other"

    safe_origin = escape(str(origin))
    safe_destination = escape(str(destination))
    safe_airline = escape(str(airline))
    safe_flight_number = escape(str(flight_number))

    safe_reference = escape(str(booking.booking_reference))
    safe_currency = escape(str(currency))

    safe_departure = escape(str(departure))
    safe_arrival = escape(str(arrival))
    safe_cabin = escape(str(cabin))

    with st.container(border=True):

        # Booking route and status

        top_left, top_right = st.columns([3, 1])

        with top_left:
            st.markdown(
                f"""
                <div class="route">
                    {safe_origin} → {safe_destination}
                </div>
                <div class="airline">
                    {safe_airline} · {safe_flight_number}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with top_right:
            st.markdown(
                f"""
                <div style="text-align:right;">
                    <span class="booking-status {status_class}">
                        {escape(status_label)}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        # Booking information

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class="booking-label">Booking Reference</div>
                <div class="booking-value">{safe_reference}</div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class="booking-label">Passengers</div>
                <div class="booking-value">{passenger_count}</div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
                <div class="booking-label">Total Amount</div>
                <div class="booking-value">
                    {safe_currency} {amount:,.2f}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.write("")

        time_col1, time_col2, time_col3 = st.columns(3)

        with time_col1:
            st.caption("Departure")
            st.write(safe_departure)

        with time_col2:
            st.caption("Arrival")
            st.write(safe_arrival)

        with time_col3:
            st.caption("Cabin")
            st.write(safe_cabin)

        # Cancellation history

        if booking.status == "demo_cancelled":

            st.markdown(
                """
                <div class="cancel-notice">
                    <b>Booking cancelled</b><br>
                    This demo booking is no longer active.
                </div>
                """,
                unsafe_allow_html=True,
            )

            if booking.cancelled_at:
                cancelled_time = booking.cancelled_at.strftime(
                    "%d %b %Y, %I:%M %p UTC"
                )

                st.caption(
                    f"Cancelled on: {cancelled_time}"
                )

            if booking.cancellation_reason:
                st.caption(
                    "Cancellation reason: "
                    + str(booking.cancellation_reason)
                )

            if booking.refund_status == "simulated_refunded":
                st.info(
                    "Simulated refund status: Refunded in demo mode. "
                    "No real money was charged or refunded."
                )

            else:
                st.caption("Refund status: Not applicable.")

        # Booking details navigation

        if st.button(
            "View Booking Details",
            key=f"view_booking_{booking.id}",
            use_container_width=True,
        ):
            st.session_state.selected_booking_id = booking.id
            st.switch_page("pages/7_Booking_Details.py")

        # Cancellation controls

        if booking.status == "demo_confirmed":

            cancel_key = f"cancel_booking_{booking.id}"

            if st.button(
                "Cancel Booking",
                key=cancel_key,
                use_container_width=True,
            ):
                st.session_state.pending_cancel_booking_id = (
                    booking.id
                )
                st.rerun()

            # Cancellation confirmation

            if (
                st.session_state.get("pending_cancel_booking_id")
                == booking.id
            ):

                st.warning(
                    "Are you sure you want to cancel this demo booking?"
                )

                reason = st.text_input(
                    "Cancellation reason (optional)",
                    key=f"cancel_reason_{booking.id}",
                    max_chars=255,
                )

                confirm_col, keep_col = st.columns(2)

                with confirm_col:

                    if st.button(
                        "Confirm Cancellation",
                        key=f"confirm_cancel_{booking.id}",
                        type="primary",
                        use_container_width=True,
                    ):

                        success, message = cancel_demo_booking(
                            booking_id=booking.id,
                            user_id=user_id,
                            reason=reason,
                        )

                        if success:
                            st.session_state.pop(
                                "pending_cancel_booking_id",
                                None,
                            )

                            st.success(message)
                            st.rerun()

                        else:
                            st.error(message)

                with keep_col:

                    if st.button(
                        "Keep Booking",
                        key=f"keep_booking_{booking.id}",
                        use_container_width=True,
                    ):

                        st.session_state.pop(
                            "pending_cancel_booking_id",
                            None,
                        )

                        st.rerun()


# --------------------------------------------------
# FOOTER NAVIGATION
# --------------------------------------------------

st.divider()

footer_col1, footer_col2 = st.columns(2)

with footer_col1:
    if st.button(
        "✈️ Search More Flights",
        use_container_width=True,
    ):
        st.switch_page("pages/1_Search_Flights.py")

with footer_col2:
    if st.button(
        "🏠 Back to Home",
        use_container_width=True,
    ):
        st.switch_page("app.py")

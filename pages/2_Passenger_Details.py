
from datetime import date, datetime, time
from decimal import Decimal, InvalidOperation
import re
import secrets

import streamlit as st
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal
from database.models import Booking, Passenger, User
from utils.auth import get_user_by_id


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Passenger Details | SkyVoyage",
    page_icon="✈️",
    layout="wide",
)

# --------------------------------------------------
# PREMIUM SKYVOYAGE STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@400;500;600;700;800&display=swap');

    .stApp {
        background:
            radial-gradient(circle at 5% 5%, rgba(76, 130, 255, 0.10), transparent 28%),
            radial-gradient(circle at 95% 15%, rgba(145, 100, 255, 0.09), transparent 25%),
            var(--background-color);
        font-family: 'DM Sans', sans-serif;
    }

    h1, h2, h3 {
        font-family: 'Manrope', sans-serif !important;
        letter-spacing: -0.7px;
    }

    .sv-hero {
        padding: 30px 32px;
        border-radius: 22px;
        margin-bottom: 24px;
        color: white;
        background: linear-gradient(120deg, #101d40 0%, #174a83 55%, #5367c9 100%);
        box-shadow: 0 12px 35px rgba(20, 50, 100, 0.18);
    }

    .sv-eyebrow {
        color: #b8d8ff;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
        text-transform: uppercase;
        margin-bottom: 9px;
    }

    .sv-hero h1 {
        color: white !important;
        font-size: clamp(28px, 4vw, 42px);
        font-weight: 800;
        margin: 0;
    }

    .sv-hero p {
        color: #e1ebff;
        font-size: 15px;
        margin-top: 10px;
        margin-bottom: 0;
    }

    .sv-section-label {
        color: #568ce8;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .sv-flight-card {
        background: var(--secondary-background-color);
        border: 1px solid rgba(120, 150, 200, 0.22);
        border-radius: 18px;
        padding: 22px;
        margin: 12px 0 20px 0;
        box-shadow: 0 5px 20px rgba(30, 60, 110, 0.06);
    }

    .sv-flight-label {
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1px;
        color: #8292aa;
        text-transform: uppercase;
        margin-bottom: 5px;
    }

    .sv-flight-value {
        font-size: 19px;
        font-weight: 800;
        color: var(--text-color);
    }

    .sv-route {
        font-size: 25px;
        font-weight: 800;
        color: #4c83e6;
    }

    .sv-price {
        font-size: 27px;
        font-weight: 800;
        color: #4c83e6;
    }

    .sv-step {
        background: var(--secondary-background-color);
        border: 1px solid rgba(120, 150, 200, 0.2);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 20px;
    }

    .sv-step strong {
        color: var(--text-color);
    }

    .sv-muted {
        color: #8292aa;
        font-size: 13px;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 11px;
        font-weight: 700;
        min-height: 44px;
        transition: all 0.2s ease;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(100deg, #2877df, #6559d9);
        border: none;
        color: white;
    }

    div.stButton > button:hover,
    div.stFormSubmitButton > button:hover {
        border-color: #6595ed;
        transform: translateY(-1px);
    }

    div[data-testid="stTextInput"] input,
    div[data-testid="stDateInput"] input,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] {
        border-radius: 10px;
    }

    @media (max-width: 768px) {
        .sv-hero {
            padding: 23px 20px;
        }

        .sv-flight-card {
            padding: 16px;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if st.session_state.user_id is None:
    st.warning("Please log in before continuing.")
    st.page_link("app.py", label="Go to Login")
    st.stop()

user = get_user_by_id(st.session_state.user_id)

if not user:
    st.session_state.user_id = None
    st.error("Your session has expired. Please log in again.")
    st.page_link("app.py", label="Return to Login")
    st.stop()


# --------------------------------------------------
# SELECTED FLIGHT
# --------------------------------------------------

draft = st.session_state.get("booking_draft")

if not draft or not draft.get("flight"):
    st.warning("No flight has been selected yet.")
    st.page_link(
        "pages/1_Search_Flights.py",
        label="Return to Flight Search",
    )
    st.stop()

flight = draft["flight"]

try:
    flight_price = Decimal(str(flight["price"]))

    if not flight_price.is_finite() or flight_price <= 0:
        raise ValueError("Invalid flight price.")

except (KeyError, ValueError, InvalidOperation):
    st.error("The selected flight has invalid pricing information.")
    st.stop()

required_flight_fields = [
    "airline_name",
    "flight_number",
    "origin_code",
    "destination_code",
    "departure",
    "arrival",
]

if any(field not in flight for field in required_flight_fields):
    st.error("Some selected flight details are missing.")
    st.stop()

departure = flight["departure"]
arrival = flight["arrival"]

if not isinstance(departure, datetime) or not isinstance(arrival, datetime):
    st.error("Invalid flight date or time information.")
    st.stop()

if arrival <= departure:
    st.error("The selected flight has invalid journey timings.")
    st.stop()


# --------------------------------------------------
# HERO
# --------------------------------------------------

st.markdown(
    """
    <div class="sv-hero">
        <div class="sv-eyebrow">SKYVOYAGE · YOUR JOURNEY</div>
        <h1>Passenger Details</h1>
        <p>
            One step closer to your journey.
            Add passenger information to continue with your booking.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# BOOKING PROGRESS
# --------------------------------------------------

st.markdown(
    """
    <div class="sv-step">
        <strong>01 · Flight selected</strong>
        &nbsp; → &nbsp;
        <strong>02 · Passenger details</strong>
        &nbsp; → &nbsp;
        <span class="sv-muted">03 · Seats & extras</span>
        &nbsp; → &nbsp;
        <span class="sv-muted">04 · Demo payment</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# FLIGHT SUMMARY
# --------------------------------------------------

st.markdown(
    '<div class="sv-section-label">YOUR JOURNEY</div>',
    unsafe_allow_html=True,
)

st.subheader("Selected flight")

with st.container(border=True):

    col1, col2, col3 = st.columns([1.1, 1.5, 1])

    with col1:
        st.markdown(
            '<div class="sv-flight-label">AIRLINE</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="sv-flight-value">{flight["airline_name"]}</div>',
            unsafe_allow_html=True,
        )
        st.caption(flight["flight_number"])

    with col2:
        st.markdown(
            '<div class="sv-flight-label">FLIGHT ROUTE</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="sv-route">{flight["origin_code"]} → '
            f'{flight["destination_code"]}</div>',
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            '<div class="sv-flight-label">DEMO FARE</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="sv-price">₹{flight_price:,.2f}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    departure_col, arrival_col = st.columns(2)

    with departure_col:
        st.markdown("**DEPARTURE**")
        st.write(departure.strftime("%d %B %Y"))
        st.write(departure.strftime("%I:%M %p"))

    with arrival_col:
        st.markdown("**ARRIVAL**")
        st.write(arrival.strftime("%d %B %Y"))
        st.write(arrival.strftime("%I:%M %p"))

st.warning(
    "DEMO FLIGHT: This is a demonstration booking. "
    "It is not a real airline reservation or ticket."
)


# --------------------------------------------------
# PASSENGER FORM
# --------------------------------------------------

created_booking = st.session_state.get("created_booking")

if not created_booking:

    st.markdown(
        '<div class="sv-section-label">TRAVELLER INFORMATION</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Who's travelling?")

    st.write(
        "Enter passenger details as they should appear "
        "on the travel document."
    )

    passenger_count = st.number_input(
        "Number of passengers",
        min_value=1,
        max_value=9,
        value=1,
        step=1,
        key="passenger_count_input",
    )

    st.caption(
        "All passengers are currently treated as adults "
        "in this demonstration version."
    )

    with st.form("passenger_details_form"):

        passenger_details = []

        for index in range(int(passenger_count)):

            st.markdown(f"### Passenger {index + 1}")

            st.caption("Personal information")

            col1, col2 = st.columns(2)

            with col1:
                full_name = st.text_input(
                    "Full name *",
                    key=f"passenger_name_{index}",
                    placeholder="Enter full name",
                )

                dob = st.date_input(
                    "Date of birth *",
                    value=date(1990, 1, 1),
                    min_value=date(1900, 1, 1),
                    max_value=date.today(),
                    key=f"passenger_dob_{index}",
                )

            with col2:
                gender = st.selectbox(
                    "Gender",
                    [
                        "Prefer not to say",
                        "Male",
                        "Female",
                        "Other",
                    ],
                    key=f"passenger_gender_{index}",
                )

                passenger_email = st.text_input(
                    "Email address",
                    value=user["email"] if index == 0 else "",
                    key=f"passenger_email_{index}",
                    placeholder="name@example.com",
                )

            passenger_phone = st.text_input(
                "Phone number",
                value=(user.get("phone") or "") if index == 0 else "",
                key=f"passenger_phone_{index}",
                placeholder="Enter phone number",
            )

            passenger_details.append(
                {
                    "full_name": full_name.strip(),
                    "date_of_birth": dob,
                    "gender": gender,
                    "email": passenger_email.strip(),
                    "phone": passenger_phone.strip(),
                }
            )

            if index < int(passenger_count) - 1:
                st.divider()

        st.divider()

        terms_accepted = st.checkbox(
            "I confirm that the passenger information entered above is accurate."
        )

        submitted = st.form_submit_button(
            "Save passenger details and create booking",
            type="primary",
            use_container_width=True,
        )

    # --------------------------------------------------
    # VALIDATION
    # --------------------------------------------------

    if submitted:

        errors = []

        for index, passenger in enumerate(passenger_details):

            if not passenger["full_name"]:
                errors.append(
                    f"Passenger {index + 1}: Full name is required."
                )

            elif len(passenger["full_name"]) < 2:
                errors.append(
                    f"Passenger {index + 1}: Name must contain at least 2 characters."
                )

            elif len(passenger["full_name"]) > 150:
                errors.append(
                    f"Passenger {index + 1}: Name must be 150 characters or fewer."
                )

            if passenger["date_of_birth"] > date.today():
                errors.append(
                    f"Passenger {index + 1}: Invalid date of birth."
                )

            email = passenger["email"]

            if email and not re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+",
                email,
            ):
                errors.append(
                    f"Passenger {index + 1}: Invalid email address."
                )

            phone = passenger["phone"]

            if phone and len(phone) > 30:
                errors.append(
                    f"Passenger {index + 1}: Phone number is too long."
                )

        if not terms_accepted:
            errors.append(
                "Please confirm that the passenger details are accurate."
            )

        if errors:
            for error in errors:
                st.error(error)

        else:

            db = SessionLocal()

            try:

                # Confirm that the account is still active.
                db_user = db.get(User, user["id"])

                if db_user is None or not db_user.is_active:
                    raise ValueError(
                        "Your account is unavailable. Please log in again."
                    )

                # Build a JSON-safe flight snapshot.
                flight_snapshot = {
                    "provider": "DEMO",
                    "airline_name": str(flight["airline_name"]),
                    "flight_number": str(flight["flight_number"]),
                    "origin_code": str(flight["origin_code"]),
                    "destination_code": str(flight["destination_code"]),
                    "departure": departure.isoformat(),
                    "arrival": arrival.isoformat(),
                    "price": str(flight_price),
                    "currency": "INR",
                    "cabin_class": str(
                        flight.get("cabin_class", "Economy")
                    ),
                    "is_demo": True,
                }

                booking_reference = (
                    "SV" + secrets.token_hex(5).upper()
                )

                booking = Booking(
                    booking_reference=booking_reference,
                    user_id=user["id"],
                    flight_offer_id=None,
                    status="demo_pending",
                    payment_status="not_required_demo",
                    total_amount=flight_price,
                    currency="INR",
                    flight_snapshot=flight_snapshot,
                )

                for passenger in passenger_details:

                    booking.passengers.append(
                        Passenger(
                            full_name=passenger["full_name"],
                            date_of_birth=datetime.combine(
                                passenger["date_of_birth"],
                                time.min,
                            ),
                            gender=passenger["gender"],
                            email=passenger["email"] or None,
                            phone=passenger["phone"] or None,
                            passenger_type="adult",
                        )
                    )

                db.add(booking)
                db.commit()
                db.refresh(booking)

                st.session_state.created_booking = {
                    "id": booking.id,
                    "reference": booking.booking_reference,
                    "amount": str(booking.total_amount),
                    "passenger_count": len(passenger_details),
                }

            except ValueError as exc:

                db.rollback()
                st.error(str(exc))

            except IntegrityError:

                db.rollback()
                st.error(
                    "A booking reference conflict occurred. "
                    "Please submit again."
                )

            except SQLAlchemyError:

                db.rollback()
                st.error(
                    "A database error occurred while saving your booking. "
                    "Please try again."
                )

            finally:
                db.close()


# --------------------------------------------------
# BOOKING REVIEW
# --------------------------------------------------

created_booking = st.session_state.get("created_booking")

if created_booking:

    st.divider()

    st.markdown(
        '<div class="sv-section-label">BOOKING CREATED</div>',
        unsafe_allow_html=True,
    )

    st.success("Your demonstration booking has been saved successfully!")

    st.subheader("Booking review")

    with st.container(border=True):

        col1, col2 = st.columns(2)

        with col1:
            st.caption("BOOKING REFERENCE")
            st.code(created_booking["reference"])

            st.caption("PASSENGERS")
            st.write(created_booking["passenger_count"])

        with col2:
            st.caption("TOTAL DEMO FARE")
            st.markdown(
                f'<div class="sv-price">'
                f'₹{Decimal(created_booking["amount"]):,.2f}'
                f'</div>',
                unsafe_allow_html=True,
            )

            st.caption("BOOKING STATUS")
            st.write("Demo — Not Ticketed")

    st.warning(
        "This is a saved demonstration booking only. "
        "No airline reservation, ticket, seat allocation, "
        "or payment has been made."
    )

    st.markdown("### What's next?")

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "Continue to seats & extras",
            type="primary",
            use_container_width=True,
        ):
            st.switch_page("pages/3_Seat_Baggage_Meals.py")

    with col2:
        if st.button(
            "Start a new flight search",
            use_container_width=True,
        ):
            st.session_state.pop("created_booking", None)
            st.session_state.pop("booking_draft", None)
            st.switch_page("pages/1_Search_Flights.py")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SkyVoyage · Demo booking experience · "
    "All flight prices and reservations are simulated."
)

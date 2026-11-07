
from decimal import Decimal

import streamlit as st

from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal
from database.models import Booking, Passenger, SeatSelection


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Seats & Extras | SkyVoyage",
    page_icon="✈️",
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

    .sv-eyebrow {
        color: #b8d8ff;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 2px;
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
        margin: 10px 0 0 0;
        font-size: 15px;
    }

    .sv-step {
        background: var(--secondary-background-color);
        border: 1px solid rgba(120,150,200,.2);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 22px;
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
        padding: 18px;
        margin-bottom: 15px;
        box-shadow: 0 5px 20px rgba(30,60,110,.05);
    }

    .sv-route {
        color: #4c83e6;
        font-size: 27px;
        font-weight: 800;
    }

    .sv-price {
        color: #4c83e6;
        font-size: 30px;
        font-weight: 800;
    }

    .sv-muted {
        color: #8292aa;
        font-size: 13px;
    }

    .sv-seat-legend {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        padding: 12px 0;
        font-size: 13px;
        color: var(--text-color);
    }

    .sv-seat-chip {
        display: inline-block;
        width: 13px;
        height: 13px;
        border-radius: 4px;
        margin-right: 5px;
        vertical-align: middle;
    }

    div.stButton > button {
        border-radius: 11px;
        min-height: 44px;
        font-weight: 700;
    }

    div.stButton > button[kind="primary"],
    div.stFormSubmitButton > button[kind="primary"] {
        background: linear-gradient(100deg, #2877df, #6559d9);
        border: none;
        color: white;
    }

    div.stFormSubmitButton > button {
        border-radius: 11px;
        min-height: 46px;
        font-weight: 700;
    }

    @media (max-width: 768px) {
        .sv-hero {
            padding: 23px 20px;
        }

        .sv-card {
            padding: 14px;
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
        <div class="sv-eyebrow">SKYVOYAGE · PERSONALIZE YOUR TRIP</div>
        <h1>Seats & Extras</h1>
        <p>
            Make your journey more comfortable.
            Choose your seat, baggage and meal preferences.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="sv-step">
        <strong>01 · Flight selected</strong>
        &nbsp; → &nbsp;
        <strong>02 · Passenger details</strong>
        &nbsp; → &nbsp;
        <strong>03 · Seats & extras</strong>
        &nbsp; → &nbsp;
        <span class="sv-muted">04 · Demo payment</span>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

user_id = st.session_state.get("user_id")

if user_id is None:
    st.warning("Please log in first.")
    st.page_link("app.py", label="Go to Login")
    st.stop()

created = st.session_state.get("created_booking")

if not created:
    st.warning("No booking found. Create a booking first.")
    st.page_link(
        "pages/1_Search_Flights.py",
        label="Search flights",
    )
    st.stop()


# --------------------------------------------------
# DATABASE
# --------------------------------------------------

db = SessionLocal()

try:
    booking = (
        db.query(Booking)
        .options(
            joinedload(Booking.passengers),
            joinedload(Booking.seats),
        )
        .filter(
            Booking.id == created["id"],
            Booking.user_id == user_id,
        )
        .first()
    )

    if not booking:
        st.error("Booking not found or access denied.")
        st.stop()

    if booking.status != "demo_pending":
        st.error("This booking is not available for demo modifications.")
        st.stop()

    passengers = sorted(
        booking.passengers,
        key=lambda passenger: passenger.id,
    )

    if not passengers:
        st.error("No passengers found for this booking.")
        st.stop()

    snapshot = booking.flight_snapshot or {}


    # --------------------------------------------------
    # FLIGHT SUMMARY
    # --------------------------------------------------

    st.markdown(
        '<div class="sv-label">YOUR JOURNEY</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Flight overview")

    with st.container(border=True):

        col1, col2, col3 = st.columns([1, 1.4, 1])

        with col1:
            st.caption("BOOKING REFERENCE")
            st.code(booking.booking_reference)

        with col2:
            st.caption("YOUR ROUTE")
            st.markdown(
                f'<div class="sv-route">'
                f'{snapshot.get("origin_code", "")} → '
                f'{snapshot.get("destination_code", "")}'
                f'</div>',
                unsafe_allow_html=True,
            )

        with col3:
            st.caption("PASSENGERS")
            st.markdown(f"### {len(passengers)}")

        st.divider()

        col1, col2 = st.columns(2)

        with col1:
            st.caption("AIRLINE")
            st.write(snapshot.get("airline_name", "Demo airline"))

        with col2:
            st.caption("FLIGHT NUMBER")
            st.write(snapshot.get("flight_number", "Demo flight"))

    st.warning(
        "DEMO SEAT MAP: This is simulated seat inventory. "
        "Selections do not reserve actual airline seats."
    )


    # --------------------------------------------------
    # DEMO SEAT INVENTORY
    # --------------------------------------------------

    seats = {}

    for row in range(1, 21):
        for letter in ["A", "B", "C", "D", "E", "F"]:

            seat = f"{row}{letter}"

            if row <= 3:
                price = Decimal("1200.00")
            elif letter in ["A", "F"]:
                price = Decimal("350.00")
            else:
                price = Decimal("0.00")

            seats[seat] = price

    existing_selections = {
        selection.passenger_id: selection
        for selection in booking.seats
    }


    # --------------------------------------------------
    # SEAT SELECTION
    # --------------------------------------------------

    st.markdown(
        '<div class="sv-label">01 · SEAT SELECTION</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Choose your preferred seats")

    st.write(
        "Select a seat individually for each passenger."
    )

    st.markdown(
        """
        <div class="sv-seat-legend">
            <span>
                <span class="sv-seat-chip" style="background:#6559d9"></span>
                Premium · ₹1,200
            </span>
            <span>
                <span class="sv-seat-chip" style="background:#2877df"></span>
                Window · ₹350
            </span>
            <span>
                <span class="sv-seat-chip" style="background:#16a085"></span>
                Standard · Free
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.caption(
        "A–F represent the six seat positions in each simulated row."
    )

    st.markdown("**Demo cabin layout**")

    with st.container(border=True):

        st.markdown(
            """
            <div style="
                text-align:center;
                padding:10px;
                border-radius:10px;
                background:rgba(70,120,220,.12);
                font-weight:800;
                letter-spacing:2px;
            ">
                ✈ FRONT OF AIRCRAFT
            </div>
            """,
            unsafe_allow_html=True,
        )

        for row in range(1, 6):

            st.markdown(f"**Row {row}**")

            col1, col2, aisle, col3, col4 = st.columns(
                [1, 1, 0.45, 1, 1]
            )

            row_seats = [
                (col1, f"{row}A"),
                (col2, f"{row}B"),
                (col3, f"{row}C"),
                (col4, f"{row}D"),
            ]

            # A visual preview only. Actual selection is made below.
            for column, seat in row_seats:
                with column:
                    if seat in seats:
                        st.markdown(
                            f"""
                            <div style="
                                text-align:center;
                                padding:7px 2px;
                                margin-bottom:7px;
                                border-radius:7px;
                                background:rgba(76,131,230,.15);
                                font-size:12px;
                                font-weight:700;
                            ">
                                {seat}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

            st.caption(
                f"Row {row}: A · B · C   |   D · E · F"
            )

        st.caption(
            "The preview is illustrative. Choose your actual seat "
            "from the passenger selection controls below."
        )


    # --------------------------------------------------
    # BAGGAGE AND MEAL OPTIONS
    # --------------------------------------------------

    st.markdown(
        '<div class="sv-label">02 · PASSENGER PREFERENCES</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Personalize each passenger's journey")

    st.caption(
        "Your previous selections will be loaded automatically."
    )

    baggage_options = {
        "Standard": Decimal("0.00"),
        "15 kg additional": Decimal("1200.00"),
        "20 kg additional": Decimal("1800.00"),
        "25 kg additional": Decimal("2500.00"),
    }

    meal_options = [
        "No preference",
        "Vegetarian",
        "Vegan",
        "Non-vegetarian",
        "Jain meal",
        "Gluten-free",
    ]

    existing_seat_numbers = {
        selection.seat_number
        for selection in booking.seats
    }

    st.markdown(
        '<div class="sv-label">03 · SAVE YOUR SELECTIONS</div>',
        unsafe_allow_html=True,
    )

    with st.form("seat_extras_form"):

        selections = {}

        for index, passenger in enumerate(passengers):

            st.markdown(
                f"### Passenger {index + 1}: {passenger.full_name}"
            )

            st.caption("Seat preference")

            previous = existing_selections.get(passenger.id)

            default_seat = (
                previous.seat_number if previous else "No seat"
            )

            seat_options = ["No seat"] + list(seats.keys())

            seat_index = (
                seat_options.index(default_seat)
                if default_seat in seat_options
                else 0
            )

            selected_seat = st.selectbox(
                "Choose your seat",
                seat_options,
                index=seat_index,
                key=f"seat_{passenger.id}",
            )

            seat_price = (
                seats[selected_seat]
                if selected_seat != "No seat"
                else Decimal("0.00")
            )

            st.caption(
                f"Selected seat charge: ₹{seat_price:,.2f}"
            )

            st.divider()

            col1, col2 = st.columns(2)

            with col1:

                previous_baggage = (
                    passenger.baggage_option or "Standard"
                )

                baggage_names = list(baggage_options.keys())

                baggage_index = (
                    baggage_names.index(previous_baggage)
                    if previous_baggage in baggage_names
                    else 0
                )

                baggage = st.selectbox(
                    "Additional baggage",
                    baggage_names,
                    index=baggage_index,
                    key=f"baggage_{passenger.id}",
                )

                st.caption(
                    f"Baggage charge: "
                    f"₹{baggage_options[baggage]:,.2f}"
                )

            with col2:

                previous_meal = (
                    passenger.meal_preference or "No preference"
                )

                meal_index = (
                    meal_options.index(previous_meal)
                    if previous_meal in meal_options
                    else 0
                )

                meal = st.selectbox(
                    "Meal preference",
                    meal_options,
                    index=meal_index,
                    key=f"meal_{passenger.id}",
                )

            selections[passenger.id] = {
                "seat": selected_seat,
                "seat_price": seat_price,
                "baggage": baggage,
                "baggage_price": baggage_options[baggage],
                "meal": meal,
            }

            if index < len(passengers) - 1:
                st.divider()

        submitted = st.form_submit_button(
            "Save seats and extras",
            type="primary",
            use_container_width=True,
        )


    # --------------------------------------------------
    # SAVE SELECTIONS
    # --------------------------------------------------

    if submitted:

        selected_seat_numbers = [
            item["seat"]
            for item in selections.values()
            if item["seat"] != "No seat"
        ]

        if len(selected_seat_numbers) != len(
            set(selected_seat_numbers)
        ):
            st.error(
                "Two passengers cannot select the same seat "
                "in this booking."
            )

        else:

            try:

                for passenger in passengers:

                    item = selections[passenger.id]

                    passenger.baggage_option = item["baggage"]
                    passenger.baggage_price = item["baggage_price"]
                    passenger.meal_preference = item["meal"]

                    existing = next(
                        (
                            selection
                            for selection in booking.seats
                            if selection.passenger_id == passenger.id
                        ),
                        None,
                    )

                    if item["seat"] == "No seat":

                        if existing:
                            db.delete(existing)

                    elif existing:

                        existing.seat_number = item["seat"]
                        existing.additional_price = item["seat_price"]
                        existing.cabin_class = snapshot.get(
                            "cabin_class",
                            "Economy",
                        )

                    else:

                        db.add(
                            SeatSelection(
                                booking_id=booking.id,
                                passenger_id=passenger.id,
                                seat_number=item["seat"],
                                cabin_class=snapshot.get(
                                    "cabin_class",
                                    "Economy",
                                ),
                                additional_price=item["seat_price"],
                            )
                        )

                base_fare = Decimal(
                    str(snapshot.get("price", "0"))
                )

                seat_total = sum(
                    (
                        item["seat_price"]
                        for item in selections.values()
                    ),
                    Decimal("0.00"),
                )

                baggage_total = sum(
                    (
                        item["baggage_price"]
                        for item in selections.values()
                    ),
                    Decimal("0.00"),
                )

                booking.total_amount = (
                    base_fare + seat_total + baggage_total
                )

                db.commit()

                st.success(
                    "Your seat and extra selections have been saved!"
                )

                st.rerun()

            except SQLAlchemyError:

                db.rollback()

                st.error(
                    "Could not save your selections. "
                    "Please try again."
                )


    # --------------------------------------------------
    # PRICE SUMMARY
    # --------------------------------------------------

    db.refresh(booking)

    st.divider()

    st.markdown(
        '<div class="sv-label">04 · FARE BREAKDOWN</div>',
        unsafe_allow_html=True,
    )

    st.subheader("Your booking total")

    base_fare = Decimal(
        str(snapshot.get("price", "0"))
    )

    seat_total = sum(
        (
            Decimal(str(selection.additional_price or 0))
            for selection in booking.seats
        ),
        Decimal("0.00"),
    )

    baggage_total = sum(
        (
            Decimal(str(passenger.baggage_price or 0))
            for passenger in booking.passengers
        ),
        Decimal("0.00"),
    )

    with st.container(border=True):

        col1, col2 = st.columns(2)

        with col1:
            st.write("Base demo fare")

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

        st.caption("TOTAL DEMO BOOKING AMOUNT")

        st.markdown(
            f'<div class="sv-price">₹{booking.total_amount:,.2f}</div>',
            unsafe_allow_html=True,
        )

    st.warning(
        "DEMO ONLY: No actual seat reservation, baggage purchase, "
        "meal order, payment or airline ticket is created."
    )


finally:
    db.close()


# --------------------------------------------------
# CONTINUE TO DEMO PAYMENT
# --------------------------------------------------

st.divider()

if st.button(
    "Continue to Demo Payment",
    type="primary",
    use_container_width=True,
):
    st.switch_page("pages/4_Demo_Payment.py")


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.caption(
    "SkyVoyage · Demo booking experience · "
    "All seat selections and extras are simulated."
)


from io import BytesIO
from xml.sax.saxutils import escape

import streamlit as st

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from database.connection import SessionLocal
from database.models import Booking


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Booking Confirmation | SkyVoyage",
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
                rgba(56, 130, 246, 0.10),
                transparent 30%
            ),
            linear-gradient(135deg, #f7f9ff, #eef3ff);
    }

    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .confirmation-hero {
        background: linear-gradient(
            120deg,
            #101d45,
            #245ca8,
            #7355b7
        );
        color: white;
        padding: 42px 25px;
        border-radius: 24px;
        text-align: center;
        box-shadow: 0 15px 40px rgba(25, 55, 110, 0.20);
        margin-bottom: 25px;
    }

    .confirmation-hero h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .confirmation-hero p {
        font-size: 1rem;
        opacity: 0.92;
    }

    .demo-label {
        display: inline-block;
        padding: 8px 16px;
        border-radius: 30px;
        background: rgba(255, 255, 255, 0.16);
        border: 1px solid rgba(255, 255, 255, 0.35);
        font-size: 0.85rem;
        font-weight: 700;
        letter-spacing: 0.5px;
        margin-bottom: 16px;
    }

    .section-heading {
        font-size: 1.35rem;
        font-weight: 800;
        color: #173b70;
        margin-top: 15px;
        margin-bottom: 12px;
    }

    .info-card {
        background: white;
        border: 1px solid #e1e9f5;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 5px 18px rgba(20, 50, 100, 0.05);
        margin-bottom: 14px;
    }

    .info-label {
        color: #64748b;
        font-size: 0.78rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .info-value {
        color: #173b70;
        font-size: 1.1rem;
        font-weight: 800;
        margin-top: 5px;
        overflow-wrap: anywhere;
    }

    .demo-warning {
        background: #fff7e8;
        border: 1px solid #f3d29a;
        color: #854d0e;
        padding: 17px;
        border-radius: 14px;
        margin-top: 18px;
        margin-bottom: 18px;
        font-size: 0.92rem;
    }

    div.stButton > button,
    div.stDownloadButton > button {
        border-radius: 12px;
        font-weight: 700;
        min-height: 46px;
    }

    @media (max-width: 768px) {
        .confirmation-hero {
            padding: 30px 15px;
        }

        .confirmation-hero h1 {
            font-size: 1.8rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def safe_text(value):
    """Escape text before placing it inside a PDF paragraph."""
    return escape(str(value if value is not None else "-"))


def flight_value(flight, *keys, default="-"):
    """Read the first available value from alternative snapshot keys."""
    for key in keys:
        value = flight.get(key)

        if value is not None and value != "":
            return str(value)

    return default


def get_passenger_seat(booking, passenger):
    """Find a passenger's seat through the booking seat selections."""
    for seat_selection in booking.seats:
        if seat_selection.passenger_id == passenger.id:
            return seat_selection.seat_number

    return "Not selected"


def create_demo_pdf(booking, payment):
    """Generate a premium, clearly labelled demo booking PDF."""

    buffer = BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "SkyVoyageTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#173B70"),
        fontSize=25,
        leading=30,
        spaceAfter=8,
    )

    subtitle_style = ParagraphStyle(
        "SkyVoyageSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#64748B"),
        fontSize=10,
        spaceAfter=8,
    )

    warning_style = ParagraphStyle(
        "DemoWarning",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#B45309"),
        fontSize=9,
        leading=13,
        spaceAfter=18,
    )

    section_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        textColor=colors.HexColor("#173B70"),
        fontSize=13,
        spaceBefore=10,
        spaceAfter=9,
    )

    cell_style = ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12,
        wordWrap="CJK",
    )

    label_style = ParagraphStyle(
        "LabelText",
        parent=cell_style,
        textColor=colors.HexColor("#475569"),
    )

    flight = booking.flight_snapshot or {}

    airline = flight_value(
        flight,
        "airline_name",
        "airline",
    )

    flight_number = flight_value(
        flight,
        "flight_number",
    )

    origin = flight_value(
        flight,
        "origin_code",
        "origin",
    )

    destination = flight_value(
        flight,
        "destination_code",
        "destination",
    )

    departure = flight_value(
        flight,
        "departure_time",
        "departure",
    )

    arrival = flight_value(
        flight,
        "arrival_time",
        "arrival",
    )

    cabin = flight_value(
        flight,
        "cabin_class",
        "cabin",
    )

    def make_table(rows, widths, header=False):
        table = Table(
            rows,
            colWidths=widths,
            repeatRows=1 if header else 0,
        )

        commands = [
            (
                "GRID",
                (0, 0),
                (-1, -1),
                0.4,
                colors.HexColor("#DCE5F0"),
            ),
            (
                "VALIGN",
                (0, 0),
                (-1, -1),
                "MIDDLE",
            ),
            (
                "LEFTPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "RIGHTPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "TOPPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
            (
                "BOTTOMPADDING",
                (0, 0),
                (-1, -1),
                7,
            ),
        ]

        if header:
            commands.extend([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#173B70"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
            ])
        else:
            commands.append(
                (
                    "BACKGROUND",
                    (0, 0),
                    (0, -1),
                    colors.HexColor("#EEF3FA"),
                )
            )

        table.setStyle(TableStyle(commands))
        return table

    story = []

    story.append(
        Paragraph("SkyVoyage", title_style)
    )

    story.append(
        Paragraph(
            "YOUR JOURNEY SUMMARY",
            subtitle_style,
        )
    )

    story.append(
        Paragraph(
            "<b>DEMO BOOKING SUMMARY — NOT A VALID AIRLINE TICKET</b>",
            warning_style,
        )
    )

    # Booking details

    story.append(
        Paragraph("Booking Details", section_style)
    )

    booking_rows = [
        [
            Paragraph("Booking reference", label_style),
            Paragraph(
                safe_text(booking.booking_reference),
                cell_style,
            ),
        ],
        [
            Paragraph("Booking status", label_style),
            Paragraph(safe_text(booking.status), cell_style),
        ],
        [
            Paragraph("Payment status", label_style),
            Paragraph(safe_text(booking.payment_status), cell_style),
        ],
        [
            Paragraph("Airline", label_style),
            Paragraph(safe_text(airline), cell_style),
        ],
        [
            Paragraph("Flight number", label_style),
            Paragraph(safe_text(flight_number), cell_style),
        ],
        [
            Paragraph("Route", label_style),
            Paragraph(
                safe_text(origin) + " to " + safe_text(destination),
                cell_style,
            ),
        ],
        [
            Paragraph("Departure", label_style),
            Paragraph(safe_text(departure), cell_style),
        ],
        [
            Paragraph("Arrival", label_style),
            Paragraph(safe_text(arrival), cell_style),
        ],
        [
            Paragraph("Cabin class", label_style),
            Paragraph(safe_text(cabin), cell_style),
        ],
        [
            Paragraph("Total amount", label_style),
            Paragraph(
                f"{safe_text(booking.currency)} "
                f"{float(booking.total_amount):,.2f}",
                cell_style,
            ),
        ],
    ]

    story.append(
        make_table(
            booking_rows,
            [48 * mm, 112 * mm],
        )
    )

    story.append(Spacer(1, 12))

    # Passenger details

    story.append(
        Paragraph("Passenger Details", section_style)
    )

    passenger_rows = [[
        Paragraph("<b>Passenger</b>", cell_style),
        Paragraph("<b>Seat</b>", cell_style),
        Paragraph("<b>Baggage</b>", cell_style),
        Paragraph("<b>Meal</b>", cell_style),
    ]]

    for passenger in booking.passengers:
        passenger_rows.append([
            Paragraph(safe_text(passenger.full_name), cell_style),
            Paragraph(
                safe_text(get_passenger_seat(booking, passenger)),
                cell_style,
            ),
            Paragraph(
                safe_text(passenger.baggage_option),
                cell_style,
            ),
            Paragraph(
                safe_text(passenger.meal_preference),
                cell_style,
            ),
        ])

    story.append(
        make_table(
            passenger_rows,
            [52 * mm, 25 * mm, 40 * mm, 43 * mm],
            header=True,
        )
    )

    story.append(Spacer(1, 12))

    # Payment details

    story.append(
        Paragraph("Demo Payment Details", section_style)
    )

    payment_rows = [
        [
            Paragraph("Gateway", label_style),
            Paragraph(safe_text(payment.gateway), cell_style),
        ],
        [
            Paragraph("Payment method", label_style),
            Paragraph(
                safe_text(payment.payment_method),
                cell_style,
            ),
        ],
        [
            Paragraph("Transaction reference", label_style),
            Paragraph(
                safe_text(payment.gateway_order_id),
                cell_style,
            ),
        ],
        [
            Paragraph("Transaction status", label_style),
            Paragraph(safe_text(payment.status), cell_style),
        ],
        [
            Paragraph("Amount", label_style),
            Paragraph(
                f"{safe_text(payment.currency)} "
                f"{float(payment.amount):,.2f}",
                cell_style,
            ),
        ],
    ]

    story.append(
        make_table(
            payment_rows,
            [48 * mm, 112 * mm],
        )
    )

    story.append(Spacer(1, 20))

    story.append(
        Paragraph(
            "<b>Important:</b> This document records a simulated "
            "SkyVoyage application transaction only. No real payment "
            "was collected, no airline inventory was reserved, and "
            "this document cannot be used for airport check-in or travel.",
            styles["BodyText"],
        )
    )

    document.build(story)

    buffer.seek(0)

    return buffer.getvalue()


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

user_id = st.session_state.get("user_id")
created_booking = st.session_state.get("created_booking")

if not user_id:
    st.warning("Please log in to view your booking.")
    st.switch_page("app.py")
    st.stop()

if not created_booking or not created_booking.get("id"):
    st.error("No booking was found.")
    st.stop()


# --------------------------------------------------
# LOAD BOOKING AND VERIFY PAYMENT
# --------------------------------------------------

db = SessionLocal()

try:
    statement = (
        select(Booking)
        .options(
            selectinload(Booking.passengers),
            selectinload(Booking.seats),
            selectinload(Booking.payments),
        )
        .where(
            Booking.id == int(created_booking["id"]),
            Booking.user_id == user_id,
        )
    )

    booking = db.execute(statement).scalar_one_or_none()

    if not booking:
        st.error("Booking not found.")
        st.stop()

    if (
        booking.status != "demo_confirmed"
        or booking.payment_status != "paid_demo"
    ):
        st.error(
            "This booking does not have a successful demo payment."
        )
        st.stop()

    successful_payments = [
        payment
        for payment in booking.payments
        if payment.status == "success_demo"
    ]

    if not successful_payments:
        st.error("No successful demo payment record was found.")
        st.stop()

    payment = max(
        successful_payments,
        key=lambda item: item.id,
    )

    flight = booking.flight_snapshot or {}

    airline = flight_value(
        flight,
        "airline_name",
        "airline",
        default="Demo Airline",
    )

    flight_number = flight_value(
        flight,
        "flight_number",
        default="DEMO",
    )

    origin = flight_value(
        flight,
        "origin_code",
        "origin",
    )

    destination = flight_value(
        flight,
        "destination_code",
        "destination",
    )

    departure = flight_value(
        flight,
        "departure_time",
        "departure",
    )

    arrival = flight_value(
        flight,
        "arrival_time",
        "arrival",
    )

    cabin = flight_value(
        flight,
        "cabin_class",
        "cabin",
    )

    pdf_bytes = create_demo_pdf(booking, payment)

    # --------------------------------------------------
    # PREMIUM CONFIRMATION HERO
    # --------------------------------------------------

    st.markdown(
        """
        <div class="confirmation-hero">
            <div class="demo-label">
                DEMO TRANSACTION SUCCESSFUL
            </div>
            <h1>✈️ Booking Confirmed!</h1>
            <p>
                Your SkyVoyage demo booking has been created successfully.
            </p>
            <p>
                <b>This is not a real airline reservation or ticket.</b>
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --------------------------------------------------
    # BOOKING SUMMARY
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">Your Booking Summary</div>',
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
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

    with col2:
        st.markdown(
            """
            <div class="info-card">
                <div class="info-label">Payment Status</div>
                <div class="info-value">Paid (Demo)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Total Amount</div>
                <div class="info-value">
                    {escape(str(booking.currency))}
                    {float(booking.total_amount):,.2f}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # --------------------------------------------------
    # FLIGHT INFORMATION
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">✈️ Flight Information</div>',
        unsafe_allow_html=True,
    )

    flight_col1, flight_col2 = st.columns(2)

    with flight_col1:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Airline</div>
                <div class="info-value">{escape(airline)}</div>
                <br>
                <div class="info-label">Flight Number</div>
                <div class="info-value">{escape(flight_number)}</div>
                <br>
                <div class="info-label">Departure Airport</div>
                <div class="info-value">{escape(origin)}</div>
                <br>
                <div class="info-label">Departure Time</div>
                <div class="info-value">{escape(departure)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with flight_col2:
        st.markdown(
            f"""
            <div class="info-card">
                <div class="info-label">Destination Airport</div>
                <div class="info-value">{escape(destination)}</div>
                <br>
                <div class="info-label">Arrival Time</div>
                <div class="info-value">{escape(arrival)}</div>
                <br>
                <div class="info-label">Cabin Class</div>
                <div class="info-value">{escape(cabin)}</div>
                <br>
                <div class="info-label">Passengers</div>
                <div class="info-value">{len(booking.passengers)}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # --------------------------------------------------
    # PASSENGER INFORMATION
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">👤 Passenger Information</div>',
        unsafe_allow_html=True,
    )

    for index, passenger in enumerate(booking.passengers, start=1):
        seat_number = get_passenger_seat(booking, passenger)

        with st.expander(
            f"Passenger {index}: {passenger.full_name}",
            expanded=True,
        ):
            passenger_col1, passenger_col2 = st.columns(2)

            with passenger_col1:
                st.write("**Passenger name:**", passenger.full_name)
                st.write("**Seat:**", seat_number)

            with passenger_col2:
                st.write(
                    "**Baggage:**",
                    passenger.baggage_option,
                )
                st.write(
                    "**Meal preference:**",
                    passenger.meal_preference,
                )

    st.divider()

    # --------------------------------------------------
    # PAYMENT INFORMATION
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">💳 Demo Transaction Details</div>',
        unsafe_allow_html=True,
    )

    payment_col1, payment_col2 = st.columns(2)

    with payment_col1:
        st.write("**Payment method:**", payment.payment_method)
        st.write("**Gateway:**", payment.gateway)

    with payment_col2:
        st.write(
            "**Transaction reference:**",
            payment.gateway_order_id,
        )
        st.write("**Transaction status:**", payment.status)

    st.divider()

    # --------------------------------------------------
    # DOWNLOAD PDF
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">📄 Download Your Summary</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "Download a PDF copy of your SkyVoyage demo booking summary."
    )

    st.download_button(
        label="⬇️ Download Demo Booking Summary (PDF)",
        data=pdf_bytes,
        file_name=(
            f"SkyVoyage_{booking.booking_reference}_DEMO.pdf"
        ),
        mime="application/pdf",
        type="primary",
        use_container_width=True,
    )

    st.markdown(
        """
        <div class="demo-warning">
            <b>Important demo notice:</b><br>
            This PDF is only a simulated booking summary.
            No real payment was collected, no airline reservation
            was made, and this document is not valid for travel.
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # --------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------

    nav_col1, nav_col2 = st.columns(2)

    with nav_col1:
        if st.button(
            "🏠 Back to Home",
            use_container_width=True,
        ):
            st.session_state.created_booking = None
            st.session_state.booking_draft = None
            st.session_state.demo_payment_success = False
            st.switch_page("app.py")

    with nav_col2:
        if st.button(
            "📋 View My Trips",
            use_container_width=True,
        ):
            st.switch_page("pages/6_My_Trips.py")

finally:
    db.close()

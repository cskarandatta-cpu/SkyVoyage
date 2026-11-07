
import streamlit as st

from datetime import datetime
from decimal import Decimal, InvalidOperation
from html import escape

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal
from database.models import Wishlist


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="My Wishlist | SkyVoyage",
    page_icon="❤️",
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

    .wishlist-hero {
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

    .wishlist-hero h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .wishlist-hero p {
        color: #e5edff;
        margin-bottom: 0;
    }

    .section-heading {
        color: #173b70;
        font-size: 1.4rem;
        font-weight: 800;
        margin-top: 15px;
        margin-bottom: 15px;
    }

    .flight-card {
        background: white;
        border: 1px solid #e1e9f5;
        border-radius: 19px;
        padding: 23px;
        box-shadow: 0 5px 18px rgba(20, 50, 100, 0.05);
        margin-bottom: 14px;
    }

    .flight-airline {
        color: #173b70;
        font-size: 1.2rem;
        font-weight: 800;
    }

    .flight-price {
        color: #245ca8;
        font-size: 1.6rem;
        font-weight: 800;
        text-align: right;
    }

    .route-code {
        color: #173b70;
        font-size: 1.65rem;
        font-weight: 800;
    }

    .route-label {
        color: #64748b;
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .route-line {
        color: #8295b2;
        font-size: 0.85rem;
        text-align: center;
    }

    .detail-label {
        color: #64748b;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
    }

    .detail-value {
        color: #173b70;
        font-weight: 700;
        margin-top: 4px;
        overflow-wrap: anywhere;
    }

    .demo-warning {
        background: #fff4db;
        border: 1px solid #f3d58f;
        color: #76500a;
        padding: 13px 16px;
        border-radius: 12px;
        margin: 15px 0;
    }

    .empty-state {
        background: white;
        border: 1px dashed #b7c9e5;
        border-radius: 20px;
        padding: 40px 20px;
        text-align: center;
        color: #64748b;
    }

    div.stButton > button {
        border-radius: 11px;
        font-weight: 700;
        min-height: 44px;
    }

    @media (max-width: 768px) {
        .wishlist-hero {
            padding: 25px 18px;
        }

        .wishlist-hero h1 {
            font-size: 1.8rem;
        }

        .route-code {
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
    st.warning("Please sign in to view your wishlist.")
    st.page_link("app.py", label="Go to Login")
    st.stop()


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="wishlist-hero">
        <h1>❤️ Your Travel Wishlist</h1>
        <p>
            Your favourite journeys, all in one place.
            Save flights and revisit them whenever you want.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

nav1, nav2 = st.columns(2)

with nav1:
    st.page_link(
        "pages/1_Search_Flights.py",
        label="✈️ Search Flights",
    )

with nav2:
    st.page_link(
        "app.py",
        label="🏠 My Account",
    )


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def display_datetime(value):
    if not value:
        return "Not available"

    try:
        parsed = datetime.fromisoformat(str(value))
        return parsed.strftime("%d %b %Y, %H:%M")

    except (ValueError, TypeError):
        return str(value)


def display_price(snapshot):
    try:
        amount = Decimal(str(snapshot.get("price", "0")))

        if not amount.is_finite():
            return "Price unavailable"

    except (InvalidOperation, ValueError, TypeError):
        return "Price unavailable"

    currency = str(snapshot.get("currency", "INR"))

    if currency == "INR":
        return f"₹{amount:,.0f}"

    return f"{currency} {amount:,.2f}"


def format_duration(duration):
    if duration is None:
        return "Not available"

    try:
        duration = int(duration)

        if duration < 0:
            return "Not available"

        hours = duration // 60
        minutes = duration % 60

        return f"{hours}h {minutes}m"

    except (ValueError, TypeError):
        return "Not available"


# --------------------------------------------------
# LOAD WISHLIST
# --------------------------------------------------

db = SessionLocal()

try:

    wishlist_items = db.scalars(
        select(Wishlist)
        .where(Wishlist.user_id == user_id)
        .order_by(Wishlist.created_at.desc())
    ).all()

    # Copy the values needed by the page before closing DB session.
    wishlist_data = [
        {
            "id": item.id,
            "origin_code": item.origin_code,
            "destination_code": item.destination_code,
            "snapshot": dict(item.flight_snapshot or {}),
        }
        for item in wishlist_items
    ]

except SQLAlchemyError:
    st.error("Unable to load your wishlist. Please try again.")
    st.stop()

finally:
    db.close()


# --------------------------------------------------
# WISHLIST SUMMARY
# --------------------------------------------------

st.divider()

total_items = len(wishlist_data)

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.metric("❤️ Saved Journeys", total_items)

with summary_col2:
    demo_count = sum(
        1
        for item in wishlist_data
        if item["snapshot"].get("is_demo")
    )

    st.metric("Demo Flight Offers", demo_count)


# --------------------------------------------------
# EMPTY WISHLIST
# --------------------------------------------------

if not wishlist_data:

    st.markdown(
        """
        <div class="empty-state">
            <h2>♡ Your wishlist is empty</h2>
            <p>
                You haven't saved any journeys yet.
                Explore flights and save the ones you love.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/1_Search_Flights.py",
        label="✈️ Explore Flights",
    )

    st.stop()


# --------------------------------------------------
# DISPLAY SAVED FLIGHTS
# --------------------------------------------------

st.markdown(
    '<div class="section-heading">Your Saved Journeys</div>',
    unsafe_allow_html=True,
)

for item in wishlist_data:

    snapshot = item["snapshot"]

    origin = snapshot.get(
        "origin_code",
        item["origin_code"],
    )

    destination = snapshot.get(
        "destination_code",
        item["destination_code"],
    )

    airline = snapshot.get(
        "airline_name",
        "Saved flight",
    )

    flight_number = snapshot.get(
        "flight_number",
        "N/A",
    )

    price = display_price(snapshot)

    departure = display_datetime(
        snapshot.get("departure")
    )

    arrival = display_datetime(
        snapshot.get("arrival")
    )

    duration = format_duration(
        snapshot.get("duration_minutes")
    )

    stops = snapshot.get("stops", 0)

    try:
        stops = int(stops)
        stops_label = (
            "Non-stop"
            if stops == 0
            else f"{stops} stop(s)"
        )
    except (ValueError, TypeError):
        stops_label = "Not available"

    with st.container(border=True):

        # ------------------------------------------
        # FLIGHT HEADER
        # ------------------------------------------

        top_left, top_right = st.columns([3, 1])

        with top_left:
            st.markdown(
                f"""
                <div class="flight-airline">
                    ✈️ {escape(str(airline))}
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.caption(f"Flight {flight_number}")

        with top_right:
            st.markdown(
                f"""
                <div class="flight-price">
                    {escape(price)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        # ------------------------------------------
        # ROUTE
        # ------------------------------------------

        route1, route2, route3 = st.columns([2, 1, 2])

        with route1:
            st.markdown(
                f"""
                <div class="route-label">Departure</div>
                <div class="route-code">
                    {escape(str(origin))}
                </div>
                <div class="route-line">
                    {escape(departure)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with route2:
            st.markdown(
                f"""
                <div style="padding-top:20px; text-align:center;">
                    <div style="color:#245ca8; font-size:1.5rem;">
                        ━ ✈ ━
                    </div>
                    <div class="route-line">
                        {escape(duration)}
                    </div>
                    <div class="route-line">
                        {escape(stops_label)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with route3:
            st.markdown(
                f"""
                <div class="route-label">Arrival</div>
                <div class="route-code">
                    {escape(str(destination))}
                </div>
                <div class="route-line">
                    {escape(arrival)}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        # ------------------------------------------
        # ADDITIONAL DETAILS
        # ------------------------------------------

        detail1, detail2, detail3 = st.columns(3)

        with detail1:
            st.markdown(
                f"""
                <div class="detail-label">Travel Date</div>
                <div class="detail-value">
                    {escape(str(snapshot.get("departure_date", "N/A")))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with detail2:
            st.markdown(
                f"""
                <div class="detail-label">Cabin Class</div>
                <div class="detail-value">
                    {escape(str(snapshot.get("cabin_class", "Economy")))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with detail3:
            st.markdown(
                f"""
                <div class="detail-label">Passengers</div>
                <div class="detail-value">
                    {escape(str(snapshot.get("passengers", 1)))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ------------------------------------------
        # RETURN JOURNEY
        # ------------------------------------------

        return_flight = snapshot.get("return_flight")

        if return_flight:

            st.divider()
            st.markdown("**↩️ Return Journey**")

            return_origin = escape(
                str(return_flight.get("origin_code", "—"))
            )

            return_destination = escape(
                str(return_flight.get("destination_code", "—"))
            )

            return_departure = escape(
                display_datetime(return_flight.get("departure"))
            )

            return_arrival = escape(
                display_datetime(return_flight.get("arrival"))
            )

            st.markdown(
                f"""
                **{return_origin}** ({return_departure})
                → **{return_destination}** ({return_arrival})
                """
            )

        # ------------------------------------------
        # DEMO WARNING
        # ------------------------------------------

        if snapshot.get("is_demo"):

            st.markdown(
                """
                <div class="demo-warning">
                    <b>DEMO FLIGHT</b><br>
                    This is a saved sample offer, not a live
                    airline reservation or ticket.
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ------------------------------------------
        # REMOVE FROM WISHLIST
        # ------------------------------------------

        if st.button(
            "🗑 Remove from Wishlist",
            key=f"remove_wishlist_{item['id']}",
            use_container_width=True,
        ):

            remove_db = SessionLocal()

            try:
                saved_item = remove_db.scalar(
                    select(Wishlist).where(
                        Wishlist.id == item["id"],
                        Wishlist.user_id == user_id,
                    )
                )

                if saved_item:
                    remove_db.delete(saved_item)
                    remove_db.commit()

                    st.success(
                        "Flight removed from your wishlist."
                    )

                st.rerun()

            except SQLAlchemyError:
                remove_db.rollback()

                st.error(
                    "Unable to remove this flight. Please try again."
                )

            finally:
                remove_db.close()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SkyVoyage Wishlist | Saved sample flights are for reference only."
)


import streamlit as st

from datetime import datetime
from html import escape

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal
from database.models import RecentSearch

from utils.flight_search import (
    get_airport_labels,
    generate_demo_flights,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Recent Searches | SkyVoyage",
    page_icon="🕘",
    layout="wide",
)


# --------------------------------------------------
# AUTHENTICATION
# --------------------------------------------------

user_id = st.session_state.get("user_id")

if user_id is None:
    st.warning("Please sign in to view your recent searches.")
    st.page_link("app.py", label="Go to Login")
    st.stop()


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

    .history-hero {
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

    .history-hero h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .history-hero p {
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

    .search-card {
        background: white;
        border: 1px solid #e1e9f5;
        border-radius: 19px;
        padding: 23px;
        box-shadow: 0 5px 18px rgba(20, 50, 100, 0.05);
        margin-bottom: 14px;
    }

    .route-heading {
        color: #173b70;
        font-size: 1.6rem;
        font-weight: 800;
    }

    .airport-name {
        color: #64748b;
        font-size: 0.88rem;
    }

    .route-arrow {
        color: #3875c5;
        font-size: 1.5rem;
        text-align: center;
    }

    .detail-label {
        color: #64748b;
        font-size: 0.74rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    .detail-value {
        color: #173b70;
        font-weight: 700;
        margin-top: 5px;
        overflow-wrap: anywhere;
    }

    .search-date {
        color: #71809a;
        font-size: 0.82rem;
        margin-top: 12px;
    }

    .trip-badge {
        display: inline-block;
        padding: 6px 12px;
        border-radius: 20px;
        background: #eaf1ff;
        color: #245ca8;
        font-size: 0.75rem;
        font-weight: 800;
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
        .history-hero {
            padding: 25px 18px;
        }

        .history-hero h1 {
            font-size: 1.8rem;
        }

        .route-heading {
            font-size: 1.3rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="history-hero">
        <h1>🕘 Recent Searches</h1>
        <p>
            Pick up where you left off.
            Revisit previous journeys and discover your next adventure.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# NAVIGATION
# --------------------------------------------------

nav1, nav2, nav3 = st.columns(3)

with nav1:
    st.page_link(
        "pages/1_Search_Flights.py",
        label="✈️ Search Flights",
    )

with nav2:
    st.page_link(
        "pages/10_Wishlist.py",
        label="❤️ Wishlist",
    )

with nav3:
    st.page_link(
        "app.py",
        label="🏠 My Account",
    )


# --------------------------------------------------
# AIRPORT LABELS
# --------------------------------------------------

airport_labels = get_airport_labels()

code_to_label = {
    code: label
    for label, code in airport_labels.items()
}


# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def format_date(value):

    if not value:
        return "Not available"

    try:
        return value.strftime("%d %b %Y")

    except (ValueError, TypeError, AttributeError):
        return str(value)


def format_datetime(value):

    if not value:
        return "Not available"

    try:
        return value.strftime("%d %b %Y, %H:%M")

    except (ValueError, TypeError, AttributeError):
        return str(value)


# --------------------------------------------------
# LOAD RECENT SEARCHES
# --------------------------------------------------

db = SessionLocal()

try:

    recent_searches = db.scalars(
        select(RecentSearch)
        .where(RecentSearch.user_id == user_id)
        .order_by(RecentSearch.created_at.desc())
    ).all()

    searches = [
        {
            "id": item.id,
            "origin_code": item.origin_code,
            "destination_code": item.destination_code,
            "departure_date": item.departure_date,
            "return_date": item.return_date,
            "passengers": item.passengers,
            "adults": item.adults,
            "children": item.children,
            "infants": item.infants,
            "cabin_class": item.cabin_class,
            "created_at": item.created_at,
        }
        for item in recent_searches
    ]

except SQLAlchemyError:

    st.error(
        "Unable to load your recent searches. Please try again."
    )

    st.stop()

finally:
    db.close()


# --------------------------------------------------
# SUMMARY
# --------------------------------------------------

st.divider()

summary_col1, summary_col2 = st.columns(2)

with summary_col1:
    st.metric(
        "🕘 Total Searches",
        len(searches),
    )

with summary_col2:

    round_trip_count = sum(
        1
        for item in searches
        if item["return_date"] is not None
    )

    st.metric(
        "↔️ Round Trips",
        round_trip_count,
    )


# --------------------------------------------------
# EMPTY SEARCH HISTORY
# --------------------------------------------------

if not searches:

    st.markdown(
        """
        <div class="empty-state">
            <h2>🕘 No recent searches yet</h2>
            <p>
                Your search history will appear here
                after you explore available sample flights.
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
# SEARCH HISTORY
# --------------------------------------------------

st.markdown(
    '<div class="section-heading">Your Search History</div>',
    unsafe_allow_html=True,
)

for item in searches:

    origin_code = item["origin_code"]
    destination_code = item["destination_code"]

    origin_name = code_to_label.get(
        origin_code,
        origin_code,
    )

    destination_name = code_to_label.get(
        destination_code,
        destination_code,
    )

    departure = item["departure_date"].date()

    return_date = (
        item["return_date"].date()
        if item["return_date"]
        else None
    )

    trip_type = (
        "Round Trip"
        if return_date
        else "One Way"
    )

    with st.container(border=True):

        # ------------------------------------------
        # ROUTE HEADER
        # ------------------------------------------

        header_left, header_right = st.columns([3, 1])

        with header_left:

            st.markdown(
                f"""
                <div class="route-heading">
                    ✈️ {escape(str(origin_code))}
                    <span style="color:#8295b2;"> → </span>
                    {escape(str(destination_code))}
                </div>
                <div class="airport-name">
                    {escape(str(origin_name))}
                    → {escape(str(destination_name))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with header_right:

            st.markdown(
                f"""
                <div style="text-align:right; padding-top:8px;">
                    <span class="trip-badge">
                        {escape(trip_type)}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        # ------------------------------------------
        # SEARCH DETAILS
        # ------------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.markdown(
                f"""
                <div class="detail-label">Departure</div>
                <div class="detail-value">
                    {escape(format_date(departure))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:

            st.markdown(
                f"""
                <div class="detail-label">Return</div>
                <div class="detail-value">
                    {escape(format_date(return_date) if return_date else "One-way")}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:

            st.markdown(
                f"""
                <div class="detail-label">Cabin Class</div>
                <div class="detail-value">
                    {escape(str(item["cabin_class"]))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.divider()

        # ------------------------------------------
        # PASSENGER DETAILS
        # ------------------------------------------

        passenger1, passenger2, passenger3 = st.columns(3)

        with passenger1:

            st.markdown(
                f"""
                <div class="detail-label">Adults</div>
                <div class="detail-value">
                    {item["adults"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with passenger2:

            st.markdown(
                f"""
                <div class="detail-label">Children</div>
                <div class="detail-value">
                    {item["children"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

        with passenger3:

            st.markdown(
                f"""
                <div class="detail-label">Infants</div>
                <div class="detail-value">
                    {item["infants"]}
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.caption(
            f"Total passengers: {item['passengers']}"
        )

        # ------------------------------------------
        # SEARCH TIMESTAMP
        # ------------------------------------------

        if item["created_at"]:

            st.markdown(
                f"""
                <div class="search-date">
                    🕒 Searched on:
                    {escape(format_datetime(item["created_at"]))}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ------------------------------------------
        # ACTIONS
        # ------------------------------------------

        action1, action2 = st.columns(2)

        # ------------------------------------------
        # REPEAT SEARCH
        # ------------------------------------------

        with action1:

            if st.button(
                "🔍 Search Again",
                key=f"repeat_search_{item['id']}",
                use_container_width=True,
                type="primary",
            ):

                try:

                    outbound = generate_demo_flights(
                        origin_code=origin_code,
                        destination_code=destination_code,
                        departure_date=departure,
                        cabin_class=item["cabin_class"],
                        adults=item["adults"],
                        children=item["children"],
                        infants=item["infants"],
                        trip_type=trip_type,
                    )

                    if return_date:

                        inbound = generate_demo_flights(
                            origin_code=destination_code,
                            destination_code=origin_code,
                            departure_date=return_date,
                            cabin_class=item["cabin_class"],
                            adults=item["adults"],
                            children=item["children"],
                            infants=item["infants"],
                            trip_type="Round-trip",
                        )

                        # Pair outbound and inbound sample offers.
                        for index, offer in enumerate(outbound):

                            if index >= len(inbound):
                                break

                            return_offer = inbound[index]

                            offer["return_flight"] = return_offer

                            offer["price"] = (
                                offer["price"]
                                + return_offer["price"]
                            )

                    if not outbound:

                        st.error(
                            "No sample flights could be generated "
                            "for this search."
                        )

                    else:

                        st.session_state.flight_results = outbound

                        st.session_state.flight_search_summary = {
                            "origin": origin_name,
                            "destination": destination_name,
                            "origin_code": origin_code,
                            "destination_code": destination_code,
                            "departure_date": departure,
                            "return_date": return_date,
                            "trip_type": trip_type,
                            "cabin_class": item["cabin_class"],
                            "adults": item["adults"],
                            "children": item["children"],
                            "infants": item["infants"],
                        }

                        st.session_state.selected_flight = None

                        st.switch_page(
                            "pages/1_Search_Flights.py"
                        )

                except (ValueError, TypeError, KeyError) as exc:

                    st.error(
                        f"Unable to repeat this search: {exc}"
                    )

        # ------------------------------------------
        # DELETE SEARCH
        # ------------------------------------------

        with action2:

            if st.button(
                "🗑 Delete History",
                key=f"delete_search_{item['id']}",
                use_container_width=True,
            ):

                delete_db = SessionLocal()

                try:

                    search_record = delete_db.scalar(
                        select(RecentSearch).where(
                            RecentSearch.id == item["id"],
                            RecentSearch.user_id == user_id,
                        )
                    )

                    if search_record:

                        delete_db.delete(search_record)
                        delete_db.commit()

                        st.success(
                            "Search removed from your history."
                        )

                    st.rerun()

                except SQLAlchemyError:

                    delete_db.rollback()

                    st.error(
                        "Unable to delete this search. Please try again."
                    )

                finally:
                    delete_db.close()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SkyVoyage | Your previous searches are saved securely "
    "to your account for convenient access."
)

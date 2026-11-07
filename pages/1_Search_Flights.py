
import streamlit as st

from datetime import date, datetime, time, timezone

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal
from database.models import Wishlist, RecentSearch

from utils.auth import get_user_by_id

from utils.flight_search import (
    get_airport_labels,
    generate_demo_flights,
    format_duration,
    format_price,
)


# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Search Flights | SkyVoyage",
    page_icon="✈️",
    layout="wide",
)


# ==================================================
# AUTHENTICATION
# ==================================================

if not st.session_state.get("user_id"):
    st.warning("Please sign in to search for flights.")
    st.page_link("app.py", label="Go to SkyVoyage login")
    st.stop()

user = get_user_by_id(st.session_state.user_id)

if user is None:
    st.session_state.user_id = None
    st.warning("Your session has expired. Please sign in again.")
    st.page_link("app.py", label="Return to login")
    st.stop()


# ==================================================
# WISHLIST FUNCTIONS
# ==================================================

def build_wishlist_snapshot(offer, summary):
    return_flight = offer.get("return_flight")
    return_snapshot = None

    if return_flight:
        return_snapshot = {
            "airline_name": return_flight["airline_name"],
            "flight_number": return_flight["flight_number"],
            "origin_code": return_flight["origin_code"],
            "destination_code": return_flight["destination_code"],
            "departure": return_flight["departure"].isoformat(),
            "arrival": return_flight["arrival"].isoformat(),
            "duration_minutes": return_flight["duration_minutes"],
            "stops": return_flight["stops"],
            "price": str(return_flight["price"]),
        }

    return {
        "offer_id": str(offer["id"]),
        "wishlist_key": (
            f"{offer['id']}|{summary['return_date'] or ''}"
        ),
        "provider": offer["provider"],
        "airline_code": offer["airline_code"],
        "airline_name": offer["airline_name"],
        "flight_number": offer["flight_number"],
        "origin_code": offer["origin_code"],
        "destination_code": offer["destination_code"],
        "departure": offer["departure"].isoformat(),
        "arrival": offer["arrival"].isoformat(),
        "departure_date": str(summary["departure_date"]),
        "return_date": (
            str(summary["return_date"])
            if summary["return_date"]
            else None
        ),
        "duration_minutes": offer["duration_minutes"],
        "stops": offer["stops"],
        "cabin_class": offer["cabin_class"],
        "price": str(offer["price"]),
        "currency": offer["currency"],
        "trip_type": offer["trip_type"],
        "passengers": offer["passengers"],
        "adults": summary["adults"],
        "children": summary["children"],
        "infants": summary["infants"],
        "return_flight": return_snapshot,
        "is_demo": True,
    }


def save_flight_to_wishlist(user_id, offer, summary):
    snapshot = build_wishlist_snapshot(offer, summary)
    db = SessionLocal()

    try:
        existing_items = db.scalars(
            select(Wishlist).where(
                Wishlist.user_id == user_id
            )
        ).all()

        for item in existing_items:
            saved_snapshot = item.flight_snapshot or {}

            if (
                saved_snapshot.get("wishlist_key")
                == snapshot["wishlist_key"]
            ):
                return False, "This flight is already in your wishlist."

        wishlist_item = Wishlist(
            user_id=user_id,
            origin_code=offer["origin_code"],
            destination_code=offer["destination_code"],
            flight_snapshot=snapshot,
        )

        db.add(wishlist_item)
        db.commit()

        return True, "Flight saved to your wishlist!"

    except SQLAlchemyError:
        db.rollback()
        return False, "Unable to save this flight. Please try again."

    finally:
        db.close()


# ==================================================
# RECENT SEARCH FUNCTION
# ==================================================

def save_recent_search(user_id, summary):
    db = SessionLocal()

    try:
        departure_datetime = datetime.combine(
            summary["departure_date"],
            time.min,
            tzinfo=timezone.utc,
        )

        return_datetime = None

        if summary["return_date"]:
            return_datetime = datetime.combine(
                summary["return_date"],
                time.min,
                tzinfo=timezone.utc,
            )

        recent_search = RecentSearch(
            user_id=user_id,
            origin_code=summary["origin_code"],
            destination_code=summary["destination_code"],
            departure_date=departure_datetime,
            return_date=return_datetime,
            passengers=(
                summary["adults"]
                + summary["children"]
                + summary["infants"]
            ),
            adults=summary["adults"],
            children=summary["children"],
            infants=summary["infants"],
            cabin_class=summary["cabin_class"],
        )

        db.add(recent_search)
        db.commit()

        history = db.scalars(
            select(RecentSearch)
            .where(RecentSearch.user_id == user_id)
            .order_by(RecentSearch.created_at.desc())
        ).all()

        for old_search in history[20:]:
            db.delete(old_search)

        db.commit()

        return True

    except SQLAlchemyError:
        db.rollback()
        return False

    finally:
        db.close()


# ==================================================
# FILTER HELPERS
# ==================================================

def matches_departure_time(offer, selected_period):
    if selected_period == "Any time":
        return True

    hour = offer["departure"].hour

    if selected_period == "Morning":
        return 5 <= hour < 12

    if selected_period == "Afternoon":
        return 12 <= hour < 17

    if selected_period == "Evening":
        return 17 <= hour < 21

    if selected_period == "Night":
        return hour >= 21 or hour < 5

    return True


def get_total_duration(offer):
    duration = offer["duration_minutes"]

    return_flight = offer.get("return_flight")

    if return_flight:
        duration += return_flight["duration_minutes"]

    return duration


# ==================================================
# PREMIUM DESIGN SYSTEM
# ==================================================

st.markdown(
    """
    <style>

    @import url(
        'https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap'
    );

    .stApp {
        background:
            radial-gradient(
                circle at 5% 0%,
                rgba(96, 165, 250, 0.13),
                transparent 28%
            ),
            linear-gradient(
                135deg,
                #f7f9ff 0%,
                #eef3ff 55%,
                #f8f9ff 100%
            );
        color: #142442;
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        max-width: 1280px;
        padding-top: 1.4rem;
        padding-bottom: 3rem;
    }

    [data-testid="stSidebar"] {
        background: #102447;
    }

    .brand {
        font-size: 27px;
        font-weight: 800;
        letter-spacing: -1px;
        color: #142b50;
    }

    .brand span {
        color: #477fe0;
    }

    .hero {
        position: relative;
        overflow: hidden;
        background:
            radial-gradient(
                circle at 90% 15%,
                rgba(145, 164, 255, 0.42),
                transparent 30%
            ),
            linear-gradient(
                120deg,
                #102447 0%,
                #214d91 62%,
                #555fc8 100%
            );
        padding: 43px 42px;
        border-radius: 25px;
        color: white;
        margin: 23px 0 20px 0;
        box-shadow: 0 18px 48px rgba(27, 59, 112, 0.18);
    }

    .hero h1 {
        color: white;
        font-size: clamp(30px, 4vw, 43px);
        font-weight: 800;
        letter-spacing: -1.5px;
        margin-bottom: 10px;
    }

    .hero p {
        color: #dce8ff;
        font-size: 16px;
        max-width: 650px;
        line-height: 1.7;
        margin-bottom: 0;
    }

    .hero-tag {
        display: inline-block;
        background: rgba(255,255,255,0.14);
        border: 1px solid rgba(255,255,255,0.22);
        color: #edf3ff;
        padding: 6px 12px;
        border-radius: 30px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 1px;
        margin-bottom: 15px;
    }

    .demo-note {
        background: #fff8e8;
        color: #79520a;
        border: 1px solid #f0d89d;
        border-radius: 12px;
        padding: 13px 16px;
        margin: 15px 0 22px 0;
        font-size: 13px;
        line-height: 1.6;
    }

    .section-heading {
        color: #172e56;
        font-size: 23px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-top: 12px;
    }

    .section-subtitle {
        color: #74819a;
        font-size: 13px;
        margin-top: -7px;
        margin-bottom: 18px;
    }

    .search-panel {
        background: rgba(255,255,255,0.84);
        border: 1px solid #e0e8f5;
        border-radius: 20px;
        padding: 10px 18px 18px 18px;
        box-shadow: 0 10px 35px rgba(28, 54, 94, 0.07);
    }

    .flight-heading {
        color: #18345f;
        font-size: 18px;
        font-weight: 800;
    }

    .flight-time {
        font-size: 25px;
        font-weight: 800;
        color: #142b50;
        letter-spacing: -0.5px;
    }

    .flight-airport {
        color: #71809a;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .big-price {
        font-size: 26px;
        font-weight: 800;
        color: #183e7b;
        letter-spacing: -0.7px;
    }

    .muted {
        color: #77859c;
        font-size: 13px;
    }

    .flight-route-line {
        color: #8aa0c2;
        font-size: 12px;
        text-align: center;
    }

    .selected-panel {
        background: linear-gradient(
            120deg,
            rgba(229, 240, 255, 0.9),
            rgba(242, 239, 255, 0.9)
        );
        border: 1px solid #d4e1f5;
        border-radius: 18px;
        padding: 20px;
        margin-top: 12px;
    }

    div.stButton > button {
        border-radius: 11px;
        font-weight: 700;
        min-height: 42px;
        transition: all 0.2s ease;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(110deg, #2458a5, #6266d8);
        border: none;
        color: white;
    }

    div.stButton > button[kind="primary"]:hover {
        background: linear-gradient(110deg, #1b478c, #5055c2);
        border: none;
        box-shadow: 0 5px 15px rgba(50, 80, 160, 0.2);
    }

    div[data-testid="stForm"] {
        background: rgba(255,255,255,0.84);
        border: 1px solid #e0e8f5;
        border-radius: 18px;
        padding: 20px;
        box-shadow: 0 8px 30px rgba(28, 54, 94, 0.05);
    }

    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-color: #e0e8f5;
        border-radius: 17px;
        background: rgba(255,255,255,0.88);
        box-shadow: 0 7px 24px rgba(28, 54, 94, 0.045);
    }

    div[data-testid="stMetric"] {
        background: rgba(255,255,255,0.8);
        border: 1px solid #e3eaf5;
        padding: 12px 15px;
        border-radius: 14px;
    }

    @media (max-width: 768px) {
        .hero {
            padding: 28px 23px;
            border-radius: 19px;
        }

        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }

        .hero h1 {
            font-size: 30px;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# TOP NAVIGATION
# ==================================================

nav1, nav2, nav3, nav4, nav5 = st.columns(
    [3, 1, 1, 1, 1]
)

with nav1:
    st.markdown(
        '<div class="brand">✈ Sky<span>Voyage</span></div>',
        unsafe_allow_html=True,
    )

with nav2:
    st.write(f"Hello, {user['full_name'].split()[0]}")

with nav3:
    st.page_link(
        "pages/10_Wishlist.py",
        label="❤️ Wishlist",
    )

with nav4:
    st.page_link(
        "pages/11_Recent_Searches.py",
        label="🕘 Recent Searches",
    )

with nav5:
    st.page_link(
        "app.py",
        label="My Account",
    )


# ==================================================
# HERO SECTION
# ==================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-tag">YOUR NEXT JOURNEY STARTS HERE</div>
        <h1>Where will life take you next?</h1>
        <p>
            Discover destinations, compare sample journeys,
            and explore the possibilities of your next adventure
            with SkyVoyage.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="demo-note">
        <strong>DEMO MODE:</strong>
        These are illustrative sample flight offers generated
        for testing. They are not live airline inventory,
        confirmed schedules or bookable tickets.
    </div>
    """,
    unsafe_allow_html=True,
)


# ==================================================
# AIRPORT CATALOGUE
# ==================================================

airport_labels = get_airport_labels()

if not airport_labels:
    st.error("No airports found in PostgreSQL.")
    st.info("Run: python -m scripts.seed_airports")
    st.stop()

airport_options = list(airport_labels.keys())


# ==================================================
# FLIGHT SEARCH FORM
# ==================================================

st.markdown(
    '<div class="section-heading">✈ Plan your journey</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-subtitle">'
    'Choose your route, dates and travel preferences.'
    '</div>',
    unsafe_allow_html=True,
)

with st.form("flight_search_form"):

    trip_type = st.radio(
        "Choose your journey",
        ["One-way", "Round-trip"],
        horizontal=True,
    )

    st.markdown("#### Your route")

    col1, col2 = st.columns(2)

    with col1:
        origin_label = st.selectbox(
            "From",
            options=airport_options,
            index=None,
            placeholder="Search departure city or airport",
        )

    with col2:
        destination_label = st.selectbox(
            "To",
            options=airport_options,
            index=None,
            placeholder="Search destination city or airport",
        )

    st.markdown("#### Travel dates")

    col3, col4 = st.columns(2)

    with col3:
        departure_date = st.date_input(
            "Departure",
            value=date.today(),
            min_value=date.today(),
        )

    with col4:
        if trip_type == "Round-trip":
            return_date = st.date_input(
                "Return",
                value=date.today(),
                min_value=date.today(),
            )
        else:
            return_date = None
            st.text_input(
                "Return",
                value="Not required for one-way",
                disabled=True,
            )

    st.markdown("#### Passengers and cabin")

    p1, p2, p3, p4 = st.columns(4)

    with p1:
        adults = st.number_input(
            "Adults",
            min_value=1,
            max_value=9,
            value=1,
            step=1,
        )

    with p2:
        children = st.number_input(
            "Children",
            min_value=0,
            max_value=8,
            value=0,
            step=1,
        )

    with p3:
        infants = st.number_input(
            "Infants",
            min_value=0,
            max_value=8,
            value=0,
            step=1,
        )

    with p4:
        cabin_class = st.selectbox(
            "Cabin class",
            [
                "Economy",
                "Premium Economy",
                "Business",
                "First Class",
            ],
        )

    st.markdown("")

    search_clicked = st.form_submit_button(
        "🔍 Search sample flights",
        type="primary",
        use_container_width=True,
    )


# ==================================================
# PROCESS SEARCH
# ==================================================

if search_clicked:

    if not origin_label or not destination_label:
        st.error(
            "Please select both departure and destination airports."
        )

    elif origin_label == destination_label:
        st.error(
            "Departure and destination airports must be different."
        )

    elif infants > adults:
        st.error(
            "The number of infants cannot exceed the number of adults."
        )

    elif trip_type == "Round-trip" and return_date is None:
        st.error("Please select a return date.")

    elif trip_type == "Round-trip" and return_date < departure_date:
        st.error(
            "Return date must be on or after the departure date."
        )

    else:
        origin_code = airport_labels[origin_label]
        destination_code = airport_labels[destination_label]

        with st.spinner("Finding sample flights for your journey..."):

            outbound = generate_demo_flights(
                origin_code=origin_code,
                destination_code=destination_code,
                departure_date=departure_date,
                cabin_class=cabin_class,
                adults=adults,
                children=children,
                infants=infants,
                trip_type=trip_type,
            )

            if trip_type == "Round-trip":

                inbound = generate_demo_flights(
                    origin_code=destination_code,
                    destination_code=origin_code,
                    departure_date=return_date,
                    cabin_class=cabin_class,
                    adults=adults,
                    children=children,
                    infants=infants,
                    trip_type=trip_type,
                )

                paired_offers = []

                for offer, return_offer in zip(outbound, inbound):
                    offer["return_flight"] = return_offer

                    offer["price"] = (
                        offer["price"] + return_offer["price"]
                    )

                    paired_offers.append(offer)

                outbound = paired_offers

            st.session_state.flight_results = outbound

            st.session_state.flight_search_summary = {
                "origin": origin_label,
                "destination": destination_label,
                "origin_code": origin_code,
                "destination_code": destination_code,
                "departure_date": departure_date,
                "return_date": return_date,
                "trip_type": trip_type,
                "cabin_class": cabin_class,
                "adults": adults,
                "children": children,
                "infants": infants,
            }

            st.session_state.selected_flight = None

            history_saved = save_recent_search(
                user_id=st.session_state.user_id,
                summary=st.session_state.flight_search_summary,
            )

            if not history_saved:
                st.warning(
                    "Your flight results are ready, but search history "
                    "could not be saved."
                )

            st.success(
                f"{len(outbound)} sample flight offers generated."
            )


# ==================================================
# FLIGHT RESULTS
# ==================================================

if "flight_results" in st.session_state:

    offers = st.session_state.flight_results
    summary = st.session_state.flight_search_summary

    st.divider()

    st.markdown(
        '<div class="section-heading">Available journeys</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f"### {summary['origin']} → {summary['destination']}"
    )

    st.caption(
        f"{summary['departure_date']} · "
        f"{summary['trip_type']} · "
        f"{summary['cabin_class']} · "
        f"{summary['adults']} adult(s), "
        f"{summary['children']} child(ren), "
        f"{summary['infants']} infant(s)"
    )

    if summary["return_date"]:
        st.caption(f"Return date: {summary['return_date']}")

    if not offers:
        st.warning(
            "No sample flights are available for this search. "
            "Please try another route or date."
        )
        st.stop()

    # ----------------------------------------------
    # RESULT OVERVIEW
    # ----------------------------------------------

    result_metric1, result_metric2, result_metric3 = st.columns(3)

    with result_metric1:
        st.metric("Sample offers", len(offers))

    with result_metric2:
        st.metric(
            "Lowest sample fare",
            format_price(min(float(x["price"]) for x in offers)),
        )

    with result_metric3:
        st.metric(
            "Airlines",
            len({x["airline_name"] for x in offers}),
        )

    # ----------------------------------------------
    # FILTERS AND SORTING
    # ----------------------------------------------

    st.markdown("### Refine your results")

    f1, f2, f3 = st.columns(3)

    with f1:
        sort_by = st.selectbox(
            "Sort by",
            [
                "Cheapest first",
                "Fastest first",
                "Earliest departure",
            ],
            key="flight_sort",
        )

    with f2:
        allowed_stops = st.multiselect(
            "Stops",
            [0, 1, 2],
            default=[0, 1, 2],
            format_func=lambda x: (
                "Non-stop" if x == 0 else f"{x} stop(s)"
            ),
            key="flight_stops",
        )

    with f3:
        airline_names = sorted({
            offer["airline_name"]
            for offer in offers
        })

        allowed_airlines = st.multiselect(
            "Airlines",
            airline_names,
            default=airline_names,
            key="flight_airlines",
        )

    # ----------------------------------------------
    # PRICE RANGE
    # ----------------------------------------------

    price_values = [
        float(offer["price"])
        for offer in offers
    ]

    min_price = min(price_values)
    max_price = max(price_values)

    st.markdown("#### 💰 Budget")

    if min_price == max_price:
        selected_price_range = (min_price, max_price)

        st.info(
            f"All sample flights are priced at "
            f"{format_price(min_price)}."
        )

    else:
        selected_price_range = st.slider(
            "Select minimum and maximum total price (INR)",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            step=max(1.0, (max_price - min_price) / 100),
            format="₹%.0f",
            key="flight_price_range",
        )

    # ----------------------------------------------
    # DEPARTURE TIME
    # ----------------------------------------------

    st.markdown("#### 🕒 Departure time")

    departure_period = st.radio(
        "Choose your preferred departure time",
        [
            "Any time",
            "Morning",
            "Afternoon",
            "Evening",
            "Night",
        ],
        horizontal=True,
        key="departure_period",
    )

    # ----------------------------------------------
    # APPLY FILTERS
    # ----------------------------------------------

    filtered_offers = [
        offer
        for offer in offers
        if (
            offer["stops"] in allowed_stops
            and offer["airline_name"] in allowed_airlines
            and selected_price_range[0]
            <= float(offer["price"])
            <= selected_price_range[1]
            and matches_departure_time(
                offer,
                departure_period,
            )
        )
    ]

    # ----------------------------------------------
    # SORT RESULTS
    # ----------------------------------------------

    if sort_by == "Cheapest first":
        filtered_offers.sort(
            key=lambda offer: float(offer["price"])
        )

    elif sort_by == "Fastest first":
        filtered_offers.sort(
            key=get_total_duration
        )

    else:
        filtered_offers.sort(
            key=lambda offer: offer["departure"]
        )

    # ----------------------------------------------
    # RESULT COUNT
    # ----------------------------------------------

    st.divider()

    st.markdown(
        f"### {len(filtered_offers)} sample flights found"
    )

    if not filtered_offers:
        st.warning(
            "No flights match your selected filters. "
            "Try changing your budget, airline, stops, "
            "or departure time."
        )

    # ----------------------------------------------
    # FLIGHT CARDS
    # ----------------------------------------------

    for offer_index, offer in enumerate(filtered_offers):

        with st.container(border=True):

            header_left, header_right = st.columns([3, 1])

            with header_left:
                st.markdown(
                    f'<div class="flight-heading">'
                    f'✈ {offer["airline_name"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                st.caption(
                    f'Flight {offer["flight_number"]} · '
                    f'{offer["cabin_class"]}'
                )

            with header_right:
                st.caption("SAMPLE FARE")
                st.markdown(
                    f'<div class="big-price">'
                    f'{format_price(offer["price"])}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            st.divider()

            left, middle, right = st.columns([2, 2, 1])

            # --------------------------------------
            # ROUTE
            # --------------------------------------

            with left:
                st.markdown(
                    f'<div class="flight-time">'
                    f'{offer["departure"].strftime("%H:%M")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f'<div class="flight-airport">'
                    f'{offer["origin_code"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                st.caption(
                    offer["departure"].strftime("%d %b %Y")
                )

                st.markdown(
                    '<div class="flight-route-line">'
                    '↓ Journey ↓'
                    '</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f'<div class="flight-time">'
                    f'{offer["arrival"].strftime("%H:%M")}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f'<div class="flight-airport">'
                    f'{offer["destination_code"]}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                st.caption(
                    offer["arrival"].strftime("%d %b %Y")
                )

            # --------------------------------------
            # DURATION AND STOPS
            # --------------------------------------

            with middle:
                st.write("**Outbound journey**")

                st.write(
                    f"⏱ {format_duration(offer['duration_minutes'])}"
                )

                if offer["stops"] == 0:
                    st.success("Non-stop")
                else:
                    st.info(f"{offer['stops']} stop(s)")

                if offer.get("return_flight"):
                    ret = offer["return_flight"]

                    st.divider()

                    st.write("**Return journey**")

                    st.write(
                        f"{ret['origin_code']} "
                        f"{ret['departure'].strftime('%H:%M')} "
                        f"→ "
                        f"{ret['destination_code']} "
                        f"{ret['arrival'].strftime('%H:%M')}"
                    )

                    st.caption(
                        f"Duration: "
                        f"{format_duration(ret['duration_minutes'])}"
                    )

                    if ret["stops"] == 0:
                        st.caption("Non-stop return")
                    else:
                        st.caption(
                            f"{ret['stops']} return stop(s)"
                        )

            # --------------------------------------
            # ACTIONS
            # --------------------------------------

            with right:
                st.caption("Total sample price")
                st.markdown(
                    f'<div class="big-price">'
                    f'{format_price(offer["price"])}'
                    f'</div>',
                    unsafe_allow_html=True,
                )

                if st.button(
                    "♡ Save to Wishlist",
                    key=f"save_flight_{offer['id']}_{offer_index}",
                    use_container_width=True,
                ):
                    saved, message = save_flight_to_wishlist(
                        user_id=st.session_state.user_id,
                        offer=offer,
                        summary=summary,
                    )

                    if saved:
                        st.success(message)
                    else:
                        st.warning(message)

                if st.button(
                    "Select flight",
                    key=f"select_flight_{offer['id']}_{offer_index}",
                    type="primary",
                    use_container_width=True,
                ):
                    st.session_state.selected_flight = offer
                    st.rerun()

    # ----------------------------------------------
    # SELECTED FLIGHT
    # ----------------------------------------------

    selected = st.session_state.get("selected_flight")

    if selected:
        st.divider()

        st.markdown("## Your selected journey")

        with st.container(border=True):
            st.success(
                f"You selected {selected['airline_name']} "
                f"({selected['flight_number']})."
            )

            st.write(
                f"**Route:** "
                f"{selected['origin_code']} → "
                f"{selected['destination_code']}"
            )

            st.write(
                f"**Departure:** "
                f"{selected['departure'].strftime('%d %b %Y, %H:%M')}"
            )

            st.write(
                f"**Arrival:** "
                f"{selected['arrival'].strftime('%d %b %Y, %H:%M')}"
            )

            if selected.get("return_flight"):
                ret = selected["return_flight"]

                st.write(
                    f"**Return:** "
                    f"{ret['origin_code']} → "
                    f"{ret['destination_code']}"
                )

                st.write(
                    f"**Return departure:** "
                    f"{ret['departure'].strftime('%d %b %Y, %H:%M')}"
                )

            st.markdown(
                f"### Total sample price: "
                f"{format_price(selected['price'])}"
            )

            st.warning(
                "This is a demo selection only. No ticket, seat, "
                "reservation or payment has been created."
            )

            if st.button(
                "Continue to passenger details",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.booking_draft = {
                    "flight": selected,
                    "search": summary,
                }

                st.success("Your flight selection is ready!")

                st.switch_page(
                    "pages/2_Passenger_Details.py"
                )

else:
    st.info(
        "Enter your journey details above and click "
        "'Search sample flights' to explore sample offers."
    )

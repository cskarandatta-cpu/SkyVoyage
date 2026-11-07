
import streamlit as st

from utils.auth import (
    register_user,
    authenticate_user,
    get_user_by_id,
)

# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SkyVoyage | Your Journey Begins",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------
# PREMIUM DESIGN SYSTEM
# --------------------------------------------------

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

:root {
    --navy: #08152f;
    --navy-light: #14264a;
    --blue: #54c3ff;
    --purple: #8171f4;
    --text: #f5f8ff;
    --muted: #b9c8e2;
    --glass: rgba(255,255,255,0.075);
    --glass-border: rgba(255,255,255,0.14);
}

.stApp {
    background:
        radial-gradient(ellipse at 12% 5%, rgba(53,116,194,.30), transparent 35%),
        radial-gradient(ellipse at 90% 30%, rgba(117,91,210,.20), transparent 35%),
        linear-gradient(135deg, #071329 0%, #101f40 55%, #192b51 100%);
    color: var(--text);
    font-family: 'DM Sans', sans-serif;
}

header[data-testid="stHeader"] {
    background: transparent;
}

.block-container {
    max-width: 1220px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

#MainMenu, footer {
    visibility: hidden;
}

.brand {
    font-size: 30px;
    font-weight: 800;
    letter-spacing: -1.3px;
    color: white;
}

.brand span {
    color: var(--blue);
}

.eyebrow {
    color: var(--blue);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    margin-bottom: 12px;
}

.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(38px, 5vw, 62px);
    line-height: 1.12;
    letter-spacing: -1px;
    color: white;
    margin: 10px 0 18px 0;
}

.hero-title span {
    color: var(--blue);
}

.hero-subtitle {
    color: var(--muted);
    font-size: 16px;
    line-height: 1.85;
    max-width: 620px;
}

.section-heading {
    color: white;
    font-size: 23px;
    font-weight: 700;
    letter-spacing: -.5px;
}

.section-caption {
    color: var(--muted);
    font-size: 13px;
}

.auth-panel {
    background: rgba(255,255,255,.085);
    border: 1px solid var(--glass-border);
    border-radius: 22px;
    padding: 24px;
    box-shadow: 0 22px 65px rgba(0,0,0,.22);
}

.feature {
    background: var(--glass);
    border: 1px solid rgba(255,255,255,.11);
    border-radius: 13px;
    padding: 15px 17px;
    margin-top: 12px;
    color: #e9f2ff;
    font-size: 14px;
    transition: .2s ease;
}

.feature:hover {
    background: rgba(255,255,255,.12);
    transform: translateY(-2px);
}

.dashboard-card {
    background: linear-gradient(
        145deg,
        rgba(255,255,255,.105),
        rgba(255,255,255,.045)
    );
    border: 1px solid var(--glass-border);
    border-radius: 18px;
    padding: 21px;
    min-height: 145px;
    margin-bottom: 10px;
    transition: .2s ease;
}

.dashboard-card:hover {
    border-color: rgba(84,195,255,.48);
    transform: translateY(-3px);
}

.dashboard-card h3 {
    color: white;
    font-size: 18px;
    margin-bottom: 9px;
}

.dashboard-card p {
    color: var(--muted);
    font-size: 13px;
    line-height: 1.6;
}

.hero-panel {
    background:
        radial-gradient(circle at 85% 20%, rgba(84,195,255,.18), transparent 32%),
        linear-gradient(120deg, rgba(255,255,255,.10), rgba(255,255,255,.035));
    border: 1px solid var(--glass-border);
    border-radius: 24px;
    padding: 30px;
    margin-top: 18px;
    margin-bottom: 28px;
}

.travel-tag {
    display: inline-block;
    color: #d9f3ff;
    background: rgba(84,195,255,.12);
    border: 1px solid rgba(84,195,255,.27);
    border-radius: 30px;
    padding: 7px 13px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 1px;
}

.muted {
    color: var(--muted);
}

.stTextInput label,
.stTextInput p,
.stSelectbox label,
.stRadio label,
.stCheckbox label {
    color: #e9f1ff !important;
}

.stTextInput input {
    background: rgba(255,255,255,.97);
    color: #10203e;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,.2);
    min-height: 43px;
}

.stTextInput input:focus {
    border-color: var(--blue);
    box-shadow: 0 0 0 2px rgba(84,195,255,.15);
}

.stButton button,
.stFormSubmitButton button {
    background: linear-gradient(105deg, #42baff, #7566ed);
    color: white;
    border: 0;
    border-radius: 11px;
    font-weight: 700;
    min-height: 44px;
    transition: .2s ease;
}

.stButton button:hover,
.stFormSubmitButton button:hover {
    color: white;
    border: 0;
    transform: translateY(-2px);
    box-shadow: 0 9px 25px rgba(69,170,255,.25);
}

.stPageLink a {
    border: 1px solid rgba(255,255,255,.13);
    border-radius: 11px;
    background: rgba(255,255,255,.055);
    color: white;
    transition: .2s ease;
}

.stPageLink a:hover {
    background: rgba(84,195,255,.12);
    border-color: rgba(84,195,255,.4);
}

div[data-testid="stForm"] {
    border: 0;
    padding: 0;
}

div[data-testid="stRadio"] > label {
    color: white !important;
}

div[data-testid="stAlert"] {
    border-radius: 12px;
}

hr {
    border-color: rgba(255,255,255,.13);
}

div[data-testid="stMetric"] {
    background: rgba(255,255,255,.065);
    border: 1px solid var(--glass-border);
    border-radius: 14px;
    padding: 14px;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: white;
}

.footer {
    text-align: center;
    color: #91a5c7;
    font-size: 12px;
    margin-top: 45px;
    padding: 18px 0;
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }

    .hero-panel {
        padding: 20px;
    }

    .auth-panel {
        padding: 18px;
    }

    .brand {
        font-size: 26px;
    }
}

</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "user_id" not in st.session_state:
    st.session_state.user_id = None

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "Login"


# --------------------------------------------------
# BRAND HEADER
# --------------------------------------------------

st.markdown(
    '<div class="brand">✈ Sky<span>Voyage</span></div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-caption">'
    'YOUR JOURNEY. YOUR WAY.'
    '</div>',
    unsafe_allow_html=True,
)


# --------------------------------------------------
# LOGGED-IN DASHBOARD
# --------------------------------------------------

if st.session_state.user_id is not None:

    user = get_user_by_id(st.session_state.user_id)

    if user is None:
        st.session_state.user_id = None
        st.rerun()

    if "full_name" not in user:
        st.error("Unable to load your account. Please sign in again.")
        st.stop()

    # Header and logout
    welcome_col, logout_col = st.columns([5, 1])

    with welcome_col:
        st.markdown(
            f'<div class="section-caption">'
            f'WELCOME BACK, {user["full_name"].upper()}'
            f'</div>',
            unsafe_allow_html=True,
        )

    with logout_col:
        if st.button("Log out", use_container_width=True):
            st.session_state.user_id = None
            st.session_state.auth_page = "Login"

            for key in [
                "booking_draft",
                "created_booking",
                "selected_flight",
                "selected_booking_id",
                "demo_payment_success",
                "flight_results",
                "flight_search_summary",
                "auth_selector",
            ]:
                st.session_state.pop(key, None)

            st.rerun()

    # Hero panel
    st.markdown("""
    <div class="hero-panel">
        <div class="travel-tag">✦ YOUR TRAVEL EXPERIENCE</div>
        <div class="hero-title">
            The world is waiting.<br>
            <span>Where will you go?</span>
        </div>
        <div class="hero-subtitle">
            Discover destinations, explore flight options, and
            manage your travel plans from one beautiful place.
            Your next adventure starts with SkyVoyage.
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Search action
    st.markdown(
        '<div class="section-heading">✈ Start your journey</div>'
        '<div class="section-caption">'
        'Find your next destination and explore available flights.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    st.page_link(
        "pages/1_Search_Flights.py",
        label="Explore and search flights",
        icon="✈️",
        use_container_width=True,
    )

    st.write("")
    st.divider()

    # Travel dashboard
    st.markdown(
        '<div class="section-heading">Your travel dashboard</div>'
        '<div class="section-caption">'
        'Everything you need to manage your journeys.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>🧳 My Trips</h3>
            <p>View your bookings, passenger details and manage your journeys.</p>
        </div>
        """, unsafe_allow_html=True)

        st.page_link(
            "pages/6_My_Trips.py",
            label="View My Trips",
            use_container_width=True,
        )

    with col2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>♡ Wishlist</h3>
            <p>Keep your favourite flight options together for later.</p>
        </div>
        """, unsafe_allow_html=True)

        st.page_link(
            "pages/10_Wishlist.py",
            label="My Wishlist",
            use_container_width=True,
        )

    with col3:
        st.markdown("""
        <div class="dashboard-card">
            <h3>◷ Recent Searches</h3>
            <p>Quickly revisit your previous flight searches.</p>
        </div>
        """, unsafe_allow_html=True)

        st.page_link(
            "pages/11_Recent_Searches.py",
            label="Recent Searches",
            use_container_width=True,
        )

    st.write("")
    st.divider()

    # Account dashboard
    st.markdown(
        '<div class="section-heading">Your account</div>'
        '<div class="section-caption">'
        'Manage your personal information and account security.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    account1, account2, account3 = st.columns(3)

    with account1:
        st.markdown("""
        <div class="dashboard-card">
            <h3>👤 My Profile</h3>
            <p>Keep your contact information up to date.</p>
        </div>
        """, unsafe_allow_html=True)

        st.page_link(
            "pages/8_My_Profile.py",
            label="Edit Profile",
            use_container_width=True,
        )

    with account2:
        st.markdown("""
        <div class="dashboard-card">
            <h3>🔐 Account Settings</h3>
            <p>Manage your password and account security.</p>
        </div>
        """, unsafe_allow_html=True)

        st.page_link(
            "pages/9_Account_Settings.py",
            label="Account Settings",
            use_container_width=True,
        )

    with account3:
        st.markdown("""
        <div class="dashboard-card">
            <h3>📋 Booking Details</h3>
            <p>Review your passenger, seat and payment information.</p>
        </div>
        """, unsafe_allow_html=True)

        st.page_link(
            "pages/6_My_Trips.py",
            label="Find My Bookings",
            use_container_width=True,
        )

    # Profile overview
    st.write("")
    st.divider()

    st.markdown(
        '<div class="section-heading">Profile overview</div>'
        '<div class="section-caption">'
        'Your registered account information.'
        '</div>',
        unsafe_allow_html=True,
    )

    profile1, profile2 = st.columns(2)

    with profile1:
        st.markdown("**Full name**")
        st.write(user["full_name"])

        st.markdown("**Email address**")
        st.write(user["email"])

    with profile2:
        st.markdown("**Phone number**")
        st.write(user.get("phone") or "Not added")

        st.markdown("**Account ID**")
        st.write(user["id"])

    st.markdown(
        '<div class="footer">'
        'SkyVoyage Demo Platform · Explore without limits'
        '</div>',
        unsafe_allow_html=True,
    )

    st.stop()


# --------------------------------------------------
# AUTHENTICATION LANDING PAGE
# --------------------------------------------------

left, right = st.columns([1.1, 0.9], gap="large")

with left:

    st.markdown('<div style="height:55px"></div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="eyebrow">✦ DISCOVER MORE. TRAVEL FURTHER.</div>'
        '<div class="hero-title">'
        'Discover the world.<br>'
        '<span>Travel beyond.</span>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="hero-subtitle">'
        'Your journey deserves something extraordinary. '
        'Discover destinations, compare flight options, and '
        'organise your next adventure with SkyVoyage.'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write("")

    st.markdown("""
    <div class="feature">🌍 &nbsp; Explore destinations worldwide</div>
    <div class="feature">✈️ &nbsp; Discover your perfect flight</div>
    <div class="feature">🔒 &nbsp; Manage your account securely</div>
    <div class="feature">🧳 &nbsp; Keep your travel plans organised</div>
    """, unsafe_allow_html=True)

    st.write("")
    st.caption("A smarter way to explore your next journey.")

with right:

    with st.container(border=True):

        st.markdown(
            '<div class="eyebrow">WELCOME ABOARD</div>'
            '<h2 style="color:white;margin-bottom:5px">'
            'Your journey starts here'
            '</h2>'
            '<p class="muted">'
            'Sign in or create an account to continue.'
            '</p>',
            unsafe_allow_html=True,
        )

        selected_page = st.radio(
            "Authentication",
            ["Login", "Create account"],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_selector",
        )

        # ------------------------------------------
        # LOGIN
        # ------------------------------------------

        if selected_page == "Login":

            st.subheader("Sign in to your account")

            with st.form("login_form"):

                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                )

                submitted = st.form_submit_button(
                    "Sign in to SkyVoyage",
                    use_container_width=True,
                )

                if submitted:

                    if not email.strip() or not password:
                        st.error("Please enter your email and password.")

                    else:
                        success, user_id, message = authenticate_user(
                            email.strip(),
                            password,
                        )

                        if success:
                            st.session_state.user_id = user_id
                            st.success(message)
                            st.rerun()

                        else:
                            st.error(message)

        # ------------------------------------------
        # REGISTRATION
        # ------------------------------------------

        else:

            st.subheader("Create your account")

            with st.form("registration_form"):

                full_name = st.text_input(
                    "Full name",
                    placeholder="Your full name",
                )

                email = st.text_input(
                    "Email address",
                    placeholder="you@example.com",
                )

                phone = st.text_input(
                    "Phone number (optional)",
                    placeholder="+91 9876543210",
                )

                password = st.text_input(
                    "Create password",
                    type="password",
                    placeholder="Minimum 8 characters",
                )

                confirm_password = st.text_input(
                    "Confirm password",
                    type="password",
                    placeholder="Re-enter your password",
                )

                st.caption(
                    "Use at least 8 characters, including uppercase, "
                    "lowercase and a number."
                )

                submitted = st.form_submit_button(
                    "Create my account",
                    use_container_width=True,
                )

                if submitted:

                    if not all([
                        full_name.strip(),
                        email.strip(),
                        password,
                        confirm_password,
                    ]):
                        st.error("Please complete all required fields.")

                    elif password != confirm_password:
                        st.error("Passwords do not match.")

                    else:
                        success, message = register_user(
                            full_name=full_name.strip(),
                            email=email.strip(),
                            password=password,
                            phone=phone.strip() or None,
                        )

                        if success:
                            st.success(message)
                            st.info(
                                "Your account is ready. "
                                "Switch to Login to sign in."
                            )

                        else:
                            st.error(message)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown(
    '<div class="footer">'
    '© 2026 SkyVoyage · Explore without limits'
    '</div>',
    unsafe_allow_html=True,
)

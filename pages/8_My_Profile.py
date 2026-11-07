
import streamlit as st

from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal
from database.models import User


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="My Profile | SkyVoyage",
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
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .profile-hero {
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

    .profile-hero h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .profile-hero p {
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

    .profile-card {
        background: white;
        border: 1px solid #e1e9f5;
        border-radius: 18px;
        padding: 23px;
        box-shadow: 0 5px 18px rgba(20, 50, 100, 0.05);
        margin-bottom: 15px;
    }

    .profile-label {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
    }

    .profile-value {
        color: #173b70;
        font-size: 1.1rem;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .profile-avatar {
        width: 72px;
        height: 72px;
        border-radius: 50%;
        background: linear-gradient(135deg, #dbeafe, #ede9fe);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        margin-bottom: 14px;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 11px;
        font-weight: 700;
        min-height: 45px;
    }

    @media (max-width: 768px) {
        .profile-hero {
            padding: 25px 18px;
        }

        .profile-hero h1 {
            font-size: 1.8rem;
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
    st.warning("Please log in to view your profile.")
    st.page_link("app.py", label="Go to Login")
    st.stop()


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="profile-hero">
        <h1>👤 My Profile</h1>
        <p>
            Manage your personal information and
            keep your SkyVoyage account up to date.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# --------------------------------------------------
# LOAD USER
# --------------------------------------------------

db = SessionLocal()

try:

    user = db.get(User, user_id)

    if not user:
        st.error("Your account could not be found.")
        st.stop()

    # --------------------------------------------------
    # ACCOUNT OVERVIEW
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">Account Overview</div>',
        unsafe_allow_html=True,
    )

    first_letter = (
        user.full_name.strip()[0].upper()
        if user.full_name and user.full_name.strip()
        else "U"
    )

    st.markdown(
        f"""
        <div class="profile-card">
            <div class="profile-avatar">{first_letter}</div>
            <div class="profile-label">Welcome back</div>
            <div class="profile-value">
                {user.full_name or "SkyVoyage Traveller"}
            </div>
            <div style="color:#64748b; margin-top:5px;">
                {user.email}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Account ID",
            user.id,
        )

    with col2:
        st.metric(
            "Account Status",
            "Active" if user.is_active else "Inactive",
        )

    with col3:
        st.metric(
            "Phone Number",
            "Added" if user.phone else "Not added",
        )

    st.divider()

    # --------------------------------------------------
    # EDIT PROFILE
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">✏️ Personal Information</div>',
        unsafe_allow_html=True,
    )

    st.caption(
        "Update your name and contact information below."
    )

    with st.form("edit_profile_form"):

        full_name = st.text_input(
            "Full name",
            value=user.full_name or "",
            max_chars=150,
            placeholder="Enter your full name",
        )

        email = st.text_input(
            "Email address",
            value=user.email or "",
            disabled=True,
            help=(
                "Email editing is disabled to protect "
                "your account identity."
            ),
        )

        phone = st.text_input(
            "Phone number",
            value=user.phone or "",
            max_chars=30,
            placeholder="Enter your phone number",
        )

        submitted = st.form_submit_button(
            "💾 Save Profile Changes",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        full_name = full_name.strip()
        phone = phone.strip()

        if not full_name:
            st.error("Please enter your full name.")

        elif len(full_name) < 2:
            st.error(
                "Your name must contain at least 2 characters."
            )

        elif len(full_name) > 150:
            st.error(
                "Your name cannot exceed 150 characters."
            )

        elif phone and len(phone) < 7:
            st.error(
                "Please enter a valid phone number."
            )

        else:

            try:
                user.full_name = full_name
                user.phone = phone or None

                db.commit()

                st.success(
                    "Your profile has been updated successfully!"
                )

                st.rerun()

            except SQLAlchemyError:
                db.rollback()

                st.error(
                    "Could not update your profile. "
                    "Please try again."
                )

    st.divider()

    # --------------------------------------------------
    # ACCOUNT INFORMATION
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">🔐 Account Information</div>',
        unsafe_allow_html=True,
    )

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-label">Account ID</div>
                <div class="profile-value">{user.id}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-label">Full Name</div>
                <div class="profile-value">
                    {user.full_name or "Not provided"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with info_col2:
        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-label">Registered Email</div>
                <div class="profile-value">
                    {user.email}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f"""
            <div class="profile-card">
                <div class="profile-label">Phone Number</div>
                <div class="profile-value">
                    {user.phone or "Not provided"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.info(
        "For security, password changes and email verification "
        "are managed separately in Account Settings."
    )

except SQLAlchemyError:
    st.error(
        "Unable to load your profile. Please try again."
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
        "← Back to Home",
        use_container_width=True,
    ):
        st.switch_page("app.py")

with nav_col2:
    if st.button(
        "🔐 Account Settings",
        use_container_width=True,
    ):
        st.switch_page("pages/9_Account_Settings.py")

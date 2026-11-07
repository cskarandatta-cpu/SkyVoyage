
import streamlit as st

from sqlalchemy.exc import SQLAlchemyError

from database.connection import SessionLocal
from database.models import User

from utils.auth import (
    verify_password,
    hash_password,
    validate_password,
)


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Account Settings | SkyVoyage",
    page_icon="⚙️",
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

    .settings-hero {
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

    .settings-hero h1 {
        color: white;
        font-size: 2.2rem;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .settings-hero p {
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

    .settings-card {
        background: white;
        border: 1px solid #e1e9f5;
        border-radius: 18px;
        padding: 23px;
        box-shadow: 0 5px 18px rgba(20, 50, 100, 0.05);
        margin-bottom: 15px;
    }

    .settings-label {
        color: #64748b;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        margin-bottom: 6px;
    }

    .settings-value {
        color: #173b70;
        font-size: 1.08rem;
        font-weight: 800;
        overflow-wrap: anywhere;
    }

    .security-item {
        background: white;
        border: 1px solid #e1e9f5;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 10px;
        color: #173b70;
        font-weight: 600;
    }

    div.stButton > button,
    div.stFormSubmitButton > button {
        border-radius: 11px;
        font-weight: 700;
        min-height: 45px;
    }

    @media (max-width: 768px) {
        .settings-hero {
            padding: 25px 18px;
        }

        .settings-hero h1 {
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
    st.warning("Please log in first.")
    st.page_link("app.py", label="Go to Login")
    st.stop()


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown(
    """
    <div class="settings-hero">
        <h1>⚙️ Account Settings</h1>
        <p>
            Manage your security and protect
            your SkyVoyage account.
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
        st.error("Account not found.")
        st.stop()

    if not user.is_active:
        st.error("Your account is disabled.")
        st.stop()

    # --------------------------------------------------
    # ACCOUNT INFORMATION
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">👤 Account Information</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            f"""
            <div class="settings-card">
                <div class="settings-label">Full Name</div>
                <div class="settings-value">
                    {user.full_name}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            f"""
            <div class="settings-card">
                <div class="settings-label">Email Address</div>
                <div class="settings-value">
                    {user.email}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    info_col1, info_col2 = st.columns(2)

    with info_col1:
        st.markdown(
            f"""
            <div class="settings-card">
                <div class="settings-label">Account ID</div>
                <div class="settings-value">
                    {user.id}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with info_col2:
        st.markdown(
            f"""
            <div class="settings-card">
                <div class="settings-label">Account Status</div>
                <div class="settings-value">
                    {"Active" if user.is_active else "Inactive"}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.divider()

    # --------------------------------------------------
    # CHANGE PASSWORD
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">🔐 Change Password</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Password requirements: at least 8 characters, "
        "one uppercase letter, one lowercase letter and "
        "one number. Maximum length: 72 UTF-8 bytes."
    )

    with st.form("change_password_form"):

        current_password = st.text_input(
            "Current password",
            type="password",
            placeholder="Enter your current password",
        )

        new_password = st.text_input(
            "New password",
            type="password",
            placeholder="Create a strong new password",
        )

        confirm_password = st.text_input(
            "Confirm new password",
            type="password",
            placeholder="Enter your new password again",
        )

        submitted = st.form_submit_button(
            "🔒 Update Password",
            type="primary",
            use_container_width=True,
        )

    if submitted:

        if not current_password:
            st.error("Please enter your current password.")

        elif not new_password:
            st.error("Please enter a new password.")

        elif not confirm_password:
            st.error("Please confirm your new password.")

        elif not user.password_hash:
            st.error(
                "This account does not have a password login. "
                "Please use its original sign-in method."
            )

        elif not verify_password(
            current_password,
            user.password_hash,
        ):
            st.error("Your current password is incorrect.")

        elif current_password == new_password:
            st.error(
                "Your new password must be different "
                "from your current password."
            )

        elif new_password != confirm_password:
            st.error("The new passwords do not match.")

        else:

            valid, message = validate_password(new_password)

            if not valid:
                st.error(message)

            else:

                try:
                    user.password_hash = hash_password(
                        new_password
                    )

                    db.commit()

                    st.success(
                        "Your password has been updated successfully!"
                    )

                    st.rerun()

                except SQLAlchemyError:
                    db.rollback()

                    st.error(
                        "Unable to update your password. "
                        "Please try again."
                    )

    st.divider()

    # --------------------------------------------------
    # SECURITY OVERVIEW
    # --------------------------------------------------

    st.markdown(
        '<div class="section-heading">🛡️ Security Overview</div>',
        unsafe_allow_html=True,
    )

    security_items = [
        "🔒 Passwords are stored using bcrypt hashing.",
        "🔐 Current password verification is required.",
        "✓ New passwords must satisfy strength requirements.",
        "🛡️ Passwords are never displayed in plain text.",
    ]

    for item in security_items:
        st.markdown(
            f"""
            <div class="security-item">
                {item}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(
        "Email changes and email verification are not currently "
        "supported in this version of SkyVoyage."
    )

except SQLAlchemyError:
    st.error("Unable to load account settings.")

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
        "👤 My Profile",
        use_container_width=True,
    ):
        st.switch_page("pages/8_My_Profile.py")

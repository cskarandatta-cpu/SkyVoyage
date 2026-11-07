import traceback
import re
import bcrypt

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from database.connection import SessionLocal
from database.models import User


def validate_email(email: str) -> bool:
    """Basic email validation."""
    pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    return bool(re.match(pattern, email.strip()))


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength and bcrypt length."""
    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if len(password.encode("utf-8")) > 72:
        return False, "Password must not exceed 72 UTF-8 bytes."

    if not re.search(r"[A-Z]", password):
        return False, "Include at least one uppercase letter."

    if not re.search(r"[a-z]", password):
        return False, "Include at least one lowercase letter."

    if not re.search(r"\d", password):
        return False, "Include at least one number."

    return True, ""


def hash_password(password: str) -> str:
    """Generate a bcrypt password hash."""
    hashed = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt(rounds=12)
    )
    return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            password_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False


def register_user(
    full_name: str,
    email: str,
    password: str,
    phone: str = None
) -> tuple[bool, str]:

    full_name = full_name.strip()
    email = email.strip().lower()
    phone = phone.strip() if phone else None

    if len(full_name) < 2:
        return False, "Please enter your full name."

    if len(full_name) > 150:
        return False, "Name must be 150 characters or fewer."

    if not validate_email(email):
        return False, "Please enter a valid email address."

    valid, message = validate_password(password)

    if not valid:
        return False, message

    db = SessionLocal()

    try:
        existing_user = db.scalar(
            select(User).where(User.email == email)
        )

        if existing_user:
            return False, "An account with this email already exists."

        user = User(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
            phone=phone,
            is_active=True
        )

        db.add(user)
        db.commit()

        return True, "Your SkyVoyage account was created successfully!"

    except IntegrityError:
        db.rollback()
        return False, "This email is already registered."

    except Exception:
        db.rollback()
        return False, "Registration failed. Please try again."

    finally:
        db.close()


def authenticate_user(
    email: str,
    password: str
) -> tuple[bool, object | None, str]:

    email = email.strip().lower()

    db = SessionLocal()

    try:
        user = db.scalar(
            select(User).where(User.email == email)
        )

        if not user or not user.password_hash:
            return False, None, "Invalid email or password."

        if not verify_password(password, user.password_hash):
            return False, None, "Invalid email or password."

        if not user.is_active:
            return False, None, "Your account is currently disabled."

        # Return only the user ID. Do not retain a detached ORM object.
        return True, user.id, "Login successful."

    except Exception as exc:
        print("AUTHENTICATION ERROR:", repr(exc))
        traceback.print_exc()
        
        return False, None, "Login failed. Please try again."
    finally:
        db.close()


def get_user_by_id(user_id: int):
    """Fetch an active user from the database."""
    db = SessionLocal()

    try:
        user = db.scalar(
            select(User).where(
                User.id == user_id,
                User.is_active.is_(True)
            )
        )

        if not user:
            return None

        return {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone
        }

    finally:
        db.close()

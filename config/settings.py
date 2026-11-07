
import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "SkyVoyage")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

    APP_SECRET_KEY = os.getenv("APP_SECRET_KEY", "")

    DATABASE_URL = os.getenv("DATABASE_URL", "")

    AMADEUS_CLIENT_ID = os.getenv("AMADEUS_CLIENT_ID", "")
    AMADEUS_CLIENT_SECRET = os.getenv("AMADEUS_CLIENT_SECRET", "")
    AMADEUS_BASE_URL = os.getenv(
        "AMADEUS_BASE_URL",
        "https://test.api.amadeus.com"
    )

    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
    RAZORPAY_WEBHOOK_SECRET = os.getenv(
        "RAZORPAY_WEBHOOK_SECRET", ""
    )

    @classmethod
    def validate(cls):
        if cls.APP_ENV == "production":
            if not cls.APP_SECRET_KEY or len(cls.APP_SECRET_KEY) < 32:
                raise ValueError(
                    "A strong APP_SECRET_KEY is required in production."
                )


settings = Settings()
settings.validate()

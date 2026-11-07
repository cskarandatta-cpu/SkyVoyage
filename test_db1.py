
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# Load environment variables
load_dotenv()

# Build a safe PostgreSQL connection URL
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT", "5432")),
    database=os.getenv("DB_NAME"),
)

try:
    engine = create_engine(database_url)

    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user, version()")
        )

        database, user, version = result.fetchone()

        print("\n================================")
        print(" SKYVOYAGE DATABASE CONNECTED!")
        print("================================")
        print(f"Database: {database}")
        print(f"User: {user}")
        print(f"Version: {version}")

except Exception as error:
    print("\nDATABASE CONNECTION FAILED!")
    print(error)

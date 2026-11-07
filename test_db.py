from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username="postgres",
    password="Root@589",
    host="localhost",
    port=5432,
    database="skyvoyage"
)

try:
    engine = create_engine(DATABASE_URL)

    with engine.connect() as connection:
        result = connection.execute(text("SELECT version()"))
        print("DATABASE CONNECTED SUCCESSFULLY!")
        print(result.scalar())

except Exception as e:
    print("DATABASE CONNECTION FAILED!")
    print(e)
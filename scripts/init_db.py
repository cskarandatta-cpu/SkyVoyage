
from database.connection import engine, Base, test_connection
from database import models


def initialize_database():
    try:
        print("Connecting to SkyVoyage PostgreSQL...")

        test_connection()

        print("Connection successful!")
        print("Creating database tables...")

        Base.metadata.create_all(bind=engine)

        print("\nSKYVOYAGE DATABASE INITIALIZED!")
        print("\nCreated tables:")

        for table in Base.metadata.sorted_tables:
            print(f"  - {table.name}")

        print("\nDatabase setup completed successfully.")

    except Exception as error:
        print("\nDATABASE INITIALIZATION FAILED!")
        print(error)
        raise

    finally:
        engine.dispose()


if __name__ == "__main__":
    initialize_database()

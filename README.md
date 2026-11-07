# ✈️ SkyVoyage – Flight Booking System

**SkyVoyage** is a Python-based flight booking web application built using Streamlit and SQLAlchemy. It provides users with an interactive platform to search flights, manage passenger details, select seats, customize travel extras, and complete demo bookings.
link https://skyvoyage.streamlit.app/

## 🌟 Features

- **User Authentication** – User registration, login, and account management.
- **Flight Search** – Search for flights based on source, destination, and travel dates.
- **Passenger Management** – Enter and manage passenger information.
- **Seat Selection** – Choose seats for individual passengers.
- **Travel Extras** – Customize baggage and meal preferences.
- **Demo Payment** – Simulated payment functionality.
- **Booking Confirmation** – View booking confirmation details.
- **User Profile** – Manage personal account information.
- **Wishlist** – Save preferred flight searches.
- **Recent Searches** – Access previously searched flights.
- **Database Management** – Store application data using SQLAlchemy ORM.

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Backend programming |
| Streamlit | Web application framework |
| SQLAlchemy | Database ORM |
| SQLite | Database (development) |
| Bcrypt | Password hashing |
| Pandas | Data processing |
| Git & GitHub | Version control |

## 📂 Project Structure


``````text
SkyVoyage/
├── app.py
├── pages/
│   ├── 1_Search_Flights.py
│   ├── 2_Passenger_Details.py
│   ├── 3_Seat_Baggage_Meals.py
│   ├── 4_Demo_Payment.py
│   ├── 5_Booking_Confirmation.py
│   ├── 6_My_Trips.py
│   ├── 7_Booking_Details.py
│   ├── 8_My_Profile.py
│   ├── 9_Account_Settings.py
│   ├── 10_Wishlist.py
│   └── 11_Recent_Searches.py
├── database/
│   ├── connection.py
│   ├── models.py
│   ├── init_db.py
│   └── seed_airports.py
├── utils/
│   ├── auth.py
│   └── flight_search.py
├── tests/
├── requirements.txt
├── .env.example
└── .gitignore



## ⚙️ Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/cskarandatta-cpu/SkyVoyage.git
```

### 2. Navigate to the Project Directory

```bash
cd SkyVoyage
```

### 3. Create a Virtual Environment

```bash
python -m venv venv
```

### 4. Activate the Virtual Environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install Dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser, usually at:

```text
http://localhost:8501
```

## 🗄️ Database

SkyVoyage uses SQLAlchemy for database operations.

The database manages application information such as:

- User accounts
- Flight searches
- Bookings
- Passenger details
- Seat selections
- Wishlist entries
- Recent searches

Database initialization is handled by the project's database configuration.

## 🔐 Security

- Passwords are hashed using Bcrypt.
- Sensitive credentials should be stored in environment variables or Streamlit secrets.
- Database files and secret configuration files should not be committed to GitHub.

## ⚠️ Important Notes

- Flight information is generated using demo data.
- Payment functionality is simulated and does not process real transactions.
- This project is intended for educational and demonstration purposes.
- Production deployment requires additional configuration, including persistent database hosting and secure payment integration.

## 🚀 Future Improvements

- Integration with real flight APIs.
- Live flight availability and pricing.
- Secure payment gateway integration.
- Email booking confirmations.
- PDF ticket generation.
- Cloud database integration.
- Improved deployment and scalability.

## 👨‍💻 Author

**Karan Datta**

GitHub: https://github.com/cskarandatta-cpu
## 📄 License

This project is developed for educational and portfolio purposes.

---

**SkyVoyage – Making Every Journey Simple! ✈️**

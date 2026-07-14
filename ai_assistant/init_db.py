import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "salon.db"


def create_connection():
    return sqlite3.connect(DB_PATH)


def create_tables(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS services (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            duration_minutes INTEGER NOT NULL,
            price REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS staff (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialty TEXT,
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS available_slots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            staff_id INTEGER,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            is_booked INTEGER DEFAULT 0,
            FOREIGN KEY (staff_id) REFERENCES staff(id)
        );

        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT NOT NULL,
            client_phone TEXT,
            service_id INTEGER NOT NULL,
            staff_id INTEGER,
            slot_id INTEGER,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (service_id) REFERENCES services(id),
            FOREIGN KEY (staff_id) REFERENCES staff(id),
            FOREIGN KEY (slot_id) REFERENCES available_slots(id)
        );

        CREATE TABLE IF NOT EXISTS faqs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            category TEXT
        );
        """
    )


def seed_data(conn):
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM services")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            """
            INSERT INTO services (name, description, duration_minutes, price)
            VALUES (?, ?, ?, ?)
            """,
            [
                ("Haircut", "Basic haircut and styling", 45, 25.0),
                ("Hair Color", "Full color treatment", 90, 75.0),
                ("Blowout", "Wash and professional blow-dry", 30, 20.0),
                ("Deep Conditioning", "Hair repair treatment", 40, 35.0),
            ],
        )

    cursor.execute("SELECT COUNT(*) FROM staff")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            """
            INSERT INTO staff (name, specialty, active)
            VALUES (?, ?, ?)
            """,
            [
                ("Ava", "Haircuts and styling", 1),
                ("Mia", "Color and highlights", 1),
                ("Sophia", "Treatments and blowouts", 1),
            ],
        )

    cursor.execute("SELECT COUNT(*) FROM faqs")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            """
            INSERT INTO faqs (question, answer, category)
            VALUES (?, ?, ?)
            """,
            [
                ("What are your opening hours?", "We are open Monday to Saturday from 9am to 6pm.", "hours"),
                ("Do I need an appointment?", "Appointments are recommended, but walk-ins are welcome when available.", "booking"),
                ("What is your cancellation policy?", "Please cancel or reschedule at least 24 hours in advance.", "policy"),
                ("Do you offer consultations?", "Yes, we offer online consultations before booking.", "consultation"),
            ],
        )

    conn.commit()


def main():
    conn = create_connection()
    try:
        create_tables(conn)
        seed_data(conn)
        print(f"Database initialized at {DB_PATH}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()   
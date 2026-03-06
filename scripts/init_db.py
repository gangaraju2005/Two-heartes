from core.database import engine, Base, SessionLocal
from core.config import settings

# Import all models to ensure they are registered with Base.metadata
from models.user import User
from models.movie import Movie
from models.theatre import Theatre
from models.screen import Screen
from models.seat import Seat
from models.show import Show
from models.booking import Booking, BookingSeat
from models.review import Review
from models.notification import Notification
from models.payment import Payment

from utils.password import get_password_hash

# INITIAL SEED DATA (Only used for first-time setup)
INITIAL_MERCHANT = {
    "name": "Merchant Test",
    "email": "merchant@test.com",
    "mobile": "7396787133",
    "password": "password123"
}

INITIAL_ADMIN = {
    "name": "Admin User",
    "email": "admin@test.com",
    "mobile": "1234567890",
    "password": "admin123"
}

def init_db():
    print("--- Database Initialization ---")
    
    # Debug: Check database connection info (masked)
    db_url = settings.DATABASE_URL
    if "@" in db_url:
        host = db_url.split("@")[-1]
        print(f"Connecting to database host: {host}")
    else:
        print(f"Connecting to database: {db_url}")

    # Debug: Check registered tables
    tables = list(Base.metadata.tables.keys())
    print(f"Registered tables for creation: {', '.join(tables)}")
    
    if not tables:
        print("WARNING: No tables found in Base.metadata. Check your model imports.")
        return

    print("Creating all database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
    except Exception as e:
        print(f"ERROR creating tables: {e}")
        return

    db = SessionLocal()
    try:
        # Check if users already exist
        user_count = db.query(User).count()
        if user_count == 0:
            print("Seeding initial users...")
            user = User(
                name=INITIAL_MERCHANT["name"],
                email=INITIAL_MERCHANT["email"],
                mobile=INITIAL_MERCHANT["mobile"],
                password_hash=get_password_hash(INITIAL_MERCHANT["password"]),
                is_merchant=True,
                is_verified=True
            )
            admin = User(
                name=INITIAL_ADMIN["name"],
                email=INITIAL_ADMIN["email"],
                mobile=INITIAL_ADMIN["mobile"],
                password_hash=get_password_hash(INITIAL_ADMIN["password"]),
                is_admin=True,
                is_verified=True
            )
            db.add_all([user, admin])
            db.commit()
            print("Successfully seeded users!")
        else:
            print(f"Users already exist ({user_count} found). Skipping seed.")
    except Exception as e:
        print(f"ERROR during seeding: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

from core.database import engine, Base
from core.config import settings

# Import all models to ensure they are registered with Base.metadata for dropping
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

def reset_db():
    print("--- Database Reset (DANGEROUS) ---")
    
    # Debug: Check database connection info (masked)
    db_url = settings.DATABASE_URL
    if "@" in db_url:
        host = db_url.split("@")[-1]
        print(f"Target database host: {host}")
    else:
        print(f"Target database: {db_url}")

    confirm = input("This will DELETE ALL DATA in the database. Are you sure? (y/N): ")
    if confirm.lower() != 'y':
        print("Reset cancelled.")
        return

    print("Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped successfully!")
    except Exception as e:
        print(f"ERROR dropping tables: {e}")

if __name__ == "__main__":
    reset_db()

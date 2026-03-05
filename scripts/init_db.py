from core.database import engine, Base, SessionLocal
from models.user import User
from models.movie import Movie
from models.theatre import Theatre
from models.screen import Screen
from models.seat import Seat
from models.show import Show
from models.booking import Booking, BookingSeat
from models.review import Review
from models.notification import Notification
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

print("Creating all database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

db = SessionLocal()
try:
    if db.query(User).count() == 0:
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
        print("Users already exist.")
finally:
    db.close()

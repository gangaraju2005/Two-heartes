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
import hmac
import hashlib

def hash_password(password: str) -> str:
    return hmac.new(b"secret", password.encode("utf-8"), hashlib.sha256).hexdigest()

print("Creating all database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created successfully!")

db = SessionLocal()
try:
    if db.query(User).count() == 0:
        print("Seeding initial users...")
        user = User(
            name="Merchant Test",
            email="merchant@test.com",
            mobile="7396787133",
            password_hash=hash_password("password123"),
            is_merchant=True,
            is_verified=True
        )
        admin = User(
            name="Admin User",
            email="admin@test.com",
            mobile="1234567890",
            password_hash=hash_password("admin123"),
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

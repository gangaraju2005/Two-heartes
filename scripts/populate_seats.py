from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.screen import Screen
from models.seat import Seat

def populate_seats():
    db = SessionLocal()
    try:
        screens = db.query(Screen).all()
        print(f"Found {len(screens)} screens. Populating seats...")

        seat_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G']
        cols_per_row = 8
        
        for screen in screens:
            # Check if seats exist
            existing = db.query(Seat).filter(Seat.screen_id == screen.id).count()
            if existing > 0:
                print(f"Screen {screen.name} (ID: {screen.id}) already has {existing} seats. Skipping.")
                continue

            seats_to_add = []
            for row in seat_rows:
                seat_type = "REGULAR"
                price = 150.0
                if row in ['D', 'E']:
                    seat_type = "PREMIUM"
                    price = 200.0
                elif row in ['F', 'G']:
                    seat_type = "RECLINER"
                    price = 250.0

                for col in range(1, cols_per_row + 1):
                    seat_num = f"{row}{col}"
                    seat = Seat(
                        screen_id=screen.id,
                        seat_number=seat_num,
                        seat_type=seat_type,
                        price=price
                    )
                    seats_to_add.append(seat)
            
            db.add_all(seats_to_add)
            print(f"Added {len(seats_to_add)} seats to Screen {screen.name}")

        db.commit()
        print("Seat population complete.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_seats()

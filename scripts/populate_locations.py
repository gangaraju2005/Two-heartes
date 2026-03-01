from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from models.theatre import Theatre
from models.user import User

def populate_locations():
    db = SessionLocal()
    try:
        # Get an admin user (or any user) to be the owner
        owner = db.query(User).first()
        if not owner:
            print("No user found to assign theatres to. Please create a user first.")
            return

        print(f"Assigning new theatres to Owner ID: {owner.id} ({owner.mobile})")

        # List of sample theatres
        sample_theatres = [
            {"name": "INOX: Varun Beach", "city": "Visakhapatnam"},
            {"name": "Cinepolis: PVP Square", "city": "Vijayawada"},
            {"name": "PVR: Preston Prime", "city": "Hyderabad"},
            {"name": "AMB Cinemas", "city": "Hyderabad"},
            {"name": "Jagadamba 70mm", "city": "Visakhapatnam"},
            {"name": "PVR: Forum Mall", "city": "Bangalore"},
        ]

        for data in sample_theatres:
            # Check if exists
            exists = db.query(Theatre).filter(Theatre.name == data["name"], Theatre.city == data["city"]).first()
            if not exists:
                theatre = Theatre(
                    name=data["name"],
                    city=data["city"],
                    owner_id=owner.id
                )
                db.add(theatre)
                print(f"Added: {data['name']} in {data['city']}")
            else:
                print(f"Skipped: {data['name']} (Already exists)")
        
        # Also, let's update any 'Unknown' cities if we want, or just leave them.
        # Let's delete 'Unknown' ones if they are just clutter, assuming they were empty test data
        unknowns = db.query(Theatre).filter(Theatre.city == "Unknown").all()
        for u in unknowns:
            u.city = "Visakhapatnam" # Update them to a default
            print(f"Updated Unknown theatre {u.id} to Visakhapatnam")
        
        db.commit()
        print("Database population complete.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_locations()

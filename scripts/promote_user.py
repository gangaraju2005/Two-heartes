from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.user import User

def promote_to_admin(mobile: str):
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.mobile == mobile).first()
        if user:
            user.is_admin = True
            db.commit()
            print(f"User {mobile} verified and promoted to Admin.")
        else:
            print(f"User {mobile} not found.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    promote_to_admin("7396787133")

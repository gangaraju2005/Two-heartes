from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from core.database import SessionLocal
# Import models to ensure they are registered
from models.user import User
from models.movie import Movie
from models.theatre import Theatre
from models.screen import Screen
from models.show import Show

def populate_shows():
    db = SessionLocal()
    try:
        # 1. Fetch Movies
        movies = db.query(Movie).all()
        if not movies:
            print("No movies found! Please add movies first.")
            return
        
        # 2. Fetch Theatres
        theatres = db.query(Theatre).all()
        print(f"Found {len(theatres)} theatres.")
        
        # 3. Define Show Times
        show_times_base = ["09:00", "12:00", "15:00", "18:00", "21:00"]
        
        shows_created_count = 0
        
        for theatre in theatres:
            print(f"Processing {theatre.name} ({theatre.city})...")
            
            # Check for screens
            screens = db.query(Screen).filter(Screen.theatre_id == theatre.id).all()
            if not screens:
                print(f"  -> No screens found. Creating default 'Screen 1'...")
                screen = Screen(
                    theatre_id=theatre.id,
                    name="Screen 1",
                    technology="Dolby Atmos",
                    total_seats=150 # 10 * 15
                )
                db.add(screen)
                db.commit()
                db.refresh(screen)
                screens = [screen]
            
            # Check if theatre already has shows (skip if it does to avoid duplicates/overpopulation for now, or just add more?)
            # Let's check show count for this theatre
            # existing_show_count = db.query(Show).join(Screen).filter(Screen.theatre_id == theatre.id).count()
            # if existing_show_count > 0:
            #    print(f"  -> Already has {existing_show_count} shows. Skipping.")
            #    continue
            
            # Create shows for next 7 days
            today = datetime.now().date()
            for day_offset in range(7):
                date = today + timedelta(days=day_offset)
                
                # For each screen
                for screen in screens:
                    # Pick 3-5 random show times
                    daily_times = random.sample(show_times_base, k=random.randint(3, 5))
                    
                    for time_str in daily_times:
                        # Combine date and time
                        dt_str = f"{date} {time_str}:00"
                        show_time = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
                        
                        # Check collision (simple check)
                        # We won't be too strict for this dummy script
                        
                        # Pick a random movie
                        movie = random.choice(movies)
                        
                        # Create Show
                        show = Show(
                            movie_id=movie.id,
                            screen_id=screen.id,
                            show_time=show_time,
                            price=random.choice([150.0, 200.0, 250.0, 300.0]) # Add price
                        )
                        db.add(show)
                        shows_created_count += 1
            
        db.commit()
        print(f"Successfully created {shows_created_count} shows across {len(theatres)} theatres.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_shows()

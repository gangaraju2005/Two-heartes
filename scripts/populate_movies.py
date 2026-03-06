from datetime import date
from sqlalchemy.orm import Session
from core.database import SessionLocal
from models.movie import Movie
from models.user import User # Ensure User is loaded for metadata awareness

def populate_movies():
    db = SessionLocal()
    try:
        sample_movies = [
            {
                "title": "Dune: Part Two",
                "language": "English",
                "duration_minutes": 166,
                "rating": 4.9,
                "release_date": date(2024, 3, 1),
                "genre": "Sci-Fi, Adventure", # Assuming we might add genre later or use description
                "poster_url": "https://image.tmdb.org/t/p/w500/1pdfLvkbY9ohJlCjQH2CZjjYVvJ.jpg" # Placeholder
            },
             {
                "title": "Civil War",
                "language": "English",
                "duration_minutes": 109,
                "rating": 4.2,
                "release_date": date(2024, 4, 12),
                 "genre": "Action, Thriller",
                 "poster_url": "https://image.tmdb.org/t/p/w500/sh7Rg8Er3tFcN9BpKIPOMvALgZd.jpg"
            },
            {
                "title": "Godzilla x Kong: The New Empire",
                "language": "English",
                "duration_minutes": 115,
                "rating": 4.5,
                "release_date": date(2024, 3, 29),
                 "genre": "Action, Sci-Fi",
                 "poster_url": "https://image.tmdb.org/t/p/w500/tMefBSflR6PGQLv7WvFPpKLZkyk.jpg"
            },
            {
                "title": "Kung Fu Panda 4",
                "language": "English",
                "duration_minutes": 94,
                "rating": 4.0,
                "release_date": date(2024, 3, 8),
                 "genre": "Animation, Action",
                 "poster_url": "https://image.tmdb.org/t/p/w500/kDp1vUBnMpe8ak4rjgl3cLELqjU.jpg"
            },
             {
                "title": "Kalki 2898 AD",
                "language": "Telugu",
                "duration_minutes": 180,
                "rating": 4.8,
                "release_date": date(2024, 6, 27),
                 "genre": "Sci-Fi, Action",
                  "poster_url": "https://m.media-amazon.com/images/S/pv-target-images/0e8c2a540ecdd6830315a6a1154460e3d047da9349d3b201b5cb355ed077dd04.jpg" # Placeholder
            },
        ]

        print("Populating Movies...")
        for data in sample_movies:
            exists = db.query(Movie).filter(Movie.title == data["title"]).first()
            if not exists:
                movie = Movie(
                    title=data["title"],
                    language=data["language"],
                    duration_minutes=data["duration_minutes"],
                    rating=data["rating"],
                    release_date=data["release_date"]
                )
                db.add(movie)
                print(f"Added: {data['title']}")
            else:
                print(f"Skipped: {data['title']} (Already exists)")
        
        db.commit()
        print("Movies population complete.")

    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_movies()

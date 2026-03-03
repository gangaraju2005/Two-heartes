from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os

from api import (
    auth,
    movies,
    shows,
    seats,
    booking,
    payments,
    admin,
    public,
    users,
    merchant,
    reviews,
    notifications,
    upload
)

app = FastAPI(
    title="Movie Ticket Backend",
    version="1.0.0"
)

# Create uploads directory if it doesn't exist
if not os.path.exists("uploads"):
    os.makedirs("uploads")
if not os.path.exists("uploads/avatars"):
    os.makedirs("uploads/avatars")

# Serve static files
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register routers
app.include_router(auth.router)
app.include_router(public.router)
app.include_router(admin.router)
app.include_router(movies.router)
app.include_router(shows.router)
app.include_router(seats.router)
app.include_router(booking.router)
app.include_router(payments.router)
app.include_router(users.router)
app.include_router(merchant.router)
app.include_router(reviews.router)
app.include_router(reviews.my_reviews_router)
app.include_router(notifications.router)
app.include_router(upload.router)


@app.get("/health")
def health_check():
    return {"status": "ok"}

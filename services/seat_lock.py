from typing import List
from core.redis import redis_client
from core.config import settings


import redis

def _seat_lock_key(show_id: int, seat_id: int) -> str:
    return f"seat_lock:{show_id}:{seat_id}"


def lock_seats(
    show_id: int,
    seat_ids: List[int],
    owner_id: str
) -> bool:
    """
    Try to lock seats for a user/session.
    Returns False if any seat is already locked.
    """
    try:
        # Step 1: check if any seat is already locked
        for seat_id in seat_ids:
            key = _seat_lock_key(show_id, seat_id)
            if redis_client.exists(key):
                return False

        # Step 2: lock all seats with TTL
        for seat_id in seat_ids:
            key = _seat_lock_key(show_id, seat_id)
            redis_client.setex(
                key,
                settings.SEAT_LOCK_TTL,
                owner_id
            )
        return True
    except Exception as e:
        print(f"Redis Lock Error: {e}")
        # Fail safe: allow booking if Redis is down
        return True


def release_seats(show_id: int, seat_ids: List[int]) -> None:
    """
    Release locked seats manually (after booking confirmation or failure).
    """
    try:
        for seat_id in seat_ids:
            key = _seat_lock_key(show_id, seat_id)
            redis_client.delete(key)
    except Exception as e:
        print(f"Redis Release Error: {e}")


def get_locked_seats(show_id: int) -> List[int]:
    """
    Return list of currently locked seat IDs for a show.
    """
    try:
        pattern = f"seat_lock:{show_id}:*"
        keys = redis_client.keys(pattern)

        locked_seats = []
        for key in keys:
            seat_id = int(key.split(":")[-1])
            locked_seats.append(seat_id)

        return locked_seats
    except Exception as e:
        print(f"Redis Get Locked Error: {e}")
        return []

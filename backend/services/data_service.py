import os
import json
from functools import wraps
from flask import session, redirect, url_for, flash, request
from backend.config import (
    PLACES_FILE, HOTELS_FILE, USERS_FILE, BOOKINGS_FILE, NOTIFICATIONS_FILE
)

TOURIST_PLACES = []
HOTELS = []


def load_datasets():
    """Load JSON datasets into memory at application startup."""
    global TOURIST_PLACES, HOTELS

    if os.path.exists(PLACES_FILE):
        try:
            with open(PLACES_FILE, 'r', encoding='utf-8') as f:
                TOURIST_PLACES = json.load(f)
        except Exception as e:
            print(f"Error loading {PLACES_FILE}: {e}")
            TOURIST_PLACES = []
    else:
        TOURIST_PLACES = []

    if os.path.exists(HOTELS_FILE):
        try:
            with open(HOTELS_FILE, 'r', encoding='utf-8') as f:
                HOTELS = json.load(f)
        except Exception as e:
            print(f"Error loading {HOTELS_FILE}: {e}")
            HOTELS = []
    else:
        HOTELS = []

    print(f"Loaded {len(TOURIST_PLACES)} tourist places and {len(HOTELS)} hotels.")


# Load immediately on module import
load_datasets()


def get_all_places():
    return TOURIST_PLACES


def get_all_hotels():
    return HOTELS


def get_place_by_id(place_id):
    for p in TOURIST_PLACES:
        if p.get('id') == place_id:
            return p
    return None


def get_hotel_by_id(hotel_id):
    for h in HOTELS:
        if h.get('id') == hotel_id:
            return h
    return None


# -------------------------------------------------------------------------
# USER ACCOUNTS DATA ACCESS
# -------------------------------------------------------------------------

def load_users():
    """Load registered users from users.json."""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading users.json: {e}")
            return []
    return []


def save_users(users):
    """Save users list to users.json."""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving users.json: {e}")
        return False


def get_user_by_email(email):
    """Lookup user by email address."""
    if not email:
        return None
    users = load_users()
    email_clean = email.strip().lower()
    for u in users:
        if u.get('email', '').strip().lower() == email_clean:
            return u
    return None


def get_user_by_id(user_id):
    """Lookup user by ID."""
    if not user_id:
        return None
    users = load_users()
    for u in users:
        if u.get('id') == user_id:
            return u
    return None


def update_user(updated_user):
    """Update user entry in users.json."""
    users = load_users()
    for i, u in enumerate(users):
        if u.get('id') == updated_user.get('id'):
            users[i] = updated_user
            return save_users(users)
    return False


def login_required(f):
    """Decorator to require login for user-specific views."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access your saved favorites and bookings.", "warning")
            return redirect(url_for('auth_bp.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


# -------------------------------------------------------------------------
# BOOKINGS & NOTIFICATIONS DATA ACCESS
# -------------------------------------------------------------------------

def load_bookings():
    """Load bookings from bookings.json."""
    if os.path.exists(BOOKINGS_FILE):
        try:
            with open(BOOKINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading bookings.json: {e}")
            return []
    return []


def save_bookings(bookings):
    """Save bookings list to bookings.json."""
    try:
        with open(BOOKINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(bookings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving bookings.json: {e}")
        return False


def get_booking_by_id(booking_id):
    """Lookup booking by reference ID."""
    bookings = load_bookings()
    for b in bookings:
        if b.get('id') == booking_id:
            return b
    return None


def load_notifications():
    """Load notifications log from email_notifications.json."""
    if os.path.exists(NOTIFICATIONS_FILE):
        try:
            with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading email_notifications.json: {e}")
            return []
    return []


def save_notifications(notifications):
    """Save notifications list to email_notifications.json."""
    try:
        with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(notifications, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving email_notifications.json: {e}")
        return False

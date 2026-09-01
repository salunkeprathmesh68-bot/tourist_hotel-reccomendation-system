import os

# Base directory for backend
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)

# Data directory
DATA_DIR = os.path.join(BACKEND_DIR, 'data')
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
BOOKINGS_FILE = os.path.join(DATA_DIR, 'bookings.json')
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, 'email_notifications.json')
PLACES_FILE = os.path.join(DATA_DIR, 'tourist_places.json')
HOTELS_FILE = os.path.join(DATA_DIR, 'hotels.json')

# Frontend template & static directories
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
TEMPLATE_DIR = os.path.join(FRONTEND_DIR, 'templates')
STATIC_DIR = os.path.join(FRONTEND_DIR, 'static')

# Secret Key
SECRET_KEY = os.environ.get('SECRET_KEY', 'smart-kolhapur-guide-secret-key-2026-viva')

# SMTP Settings
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL', 'bookings@kolhapur.gov.in')

CATEGORIES = [
    {"id": "all", "name": "All Destinations", "icon": "fa-globe"},
    {"id": "religion", "name": "Spiritual & Temples", "icon": "fa-om"},
    {"id": "history", "name": "Forts & Heritage", "icon": "fa-monument"},
    {"id": "nature", "name": "Lakes & Greenery", "icon": "fa-leaf"},
    {"id": "culture", "name": "Arts & Museums", "icon": "fa-masks-theater"},
    {"id": "adventure", "name": "Safaris & Ghats", "icon": "fa-mountain"}
]

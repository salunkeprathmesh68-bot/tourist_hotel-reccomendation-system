"""
Smart Kolhapur Guide - Application Entry Point
Forwards execution to the modular backend application.
"""
from backend.app import app, create_app
from backend.config import CATEGORIES, USERS_FILE, BOOKINGS_FILE, NOTIFICATIONS_FILE
from backend.services.data_service import (
    get_all_places, get_all_hotels, get_place_by_id, get_hotel_by_id,
    load_users, save_users, get_user_by_email, load_bookings, save_bookings,
    get_booking_by_id, load_notifications, save_notifications,
    TOURIST_PLACES, HOTELS
)
from backend.services.recommendation_service import (
    haversine_distance, recommend_hotels
)
from backend.services.notification_service import (
    generate_and_dispatch_notification, DESTINATION_TRAVEL_INSTRUCTIONS
)

if __name__ == '__main__':
    print("============================================================")
    print(" [START] SMART KOLHAPUR GUIDE - Web Application Starting")
    print(" [INFO]  District: Kolhapur, Maharashtra, India")
    print(" [INFO]  Running on: http://127.0.0.1:5000")
    print("============================================================")
    app.run(debug=True, host='127.0.0.1', port=5000)

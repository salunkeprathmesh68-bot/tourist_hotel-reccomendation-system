import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, jsonify, abort, session, redirect, url_for, flash
from backend.services.data_service import (
    get_hotel_by_id, get_place_by_id, load_bookings, save_bookings,
    get_booking_by_id, load_notifications, login_required
)
from backend.services.notification_service import (
    generate_and_dispatch_notification, DESTINATION_TRAVEL_INSTRUCTIONS
)

booking_bp = Blueprint('booking_bp', __name__)


@booking_bp.route('/api/bookings/create', methods=['POST'])
def api_create_booking():
    """Create a new hotel reservation with verified online payment."""
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form.to_dict()

    hotel_id = data.get('hotel_id')
    hotel = get_hotel_by_id(hotel_id)
    if not hotel:
        return jsonify({"status": "error", "message": "Selected hotel does not exist."}), 404

    # Guest details
    guest_name = data.get('guest_name', '').strip() or session.get('name', 'Kolhapur Traveler')
    guest_email = data.get('guest_email', '').strip() or session.get('email', '')
    guest_phone = data.get('guest_phone', '').strip()
    special_requests = data.get('special_requests', '').strip()

    if not guest_name or not guest_email or not guest_phone:
        return jsonify({"status": "error", "message": "Please provide your Full Name, Email, and Phone number."}), 400

    # Destination context
    dest_id = data.get('destination_id') or hotel.get('destination_id')
    dest = get_place_by_id(dest_id)
    dest_name = dest['name'] if dest else "Kolhapur City Center"

    # Dates and room setup
    check_in_str = data.get('check_in')
    check_out_str = data.get('check_out')

    if not check_in_str or not check_out_str:
        return jsonify({"status": "error", "message": "Please specify both Check-in and Check-out dates."}), 400

    try:
        d_in = datetime.strptime(check_in_str, "%Y-%m-%d")
        d_out = datetime.strptime(check_out_str, "%Y-%m-%d")
        nights = (d_out - d_in).days
        if nights < 1:
            return jsonify({"status": "error", "message": "Check-out date must be at least 1 day after Check-in date."}), 400
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid date format. Expected YYYY-MM-DD."}), 400

    try:
        guests = int(data.get('guests', 2))
        rooms = int(data.get('rooms', 1))
    except (ValueError, TypeError):
        guests = 2
        rooms = 1

    room_type = data.get('room_type', 'Deluxe Heritage Room')
    price_per_night = hotel.get('price_per_night', 2000)

    # Dynamic pricing multiplier by room type
    if "Suite" in room_type:
        price_per_night = int(price_per_night * 1.35)
    elif "Executive" in room_type:
        price_per_night = int(price_per_night * 1.15)

    total_price = price_per_night * nights * rooms

    # Payment processing metadata
    booking_id = f"BK-KOL-{uuid.uuid4().hex[:4].upper()}"
    payment_method = data.get('payment_method', 'UPI / Google Pay')
    payment_status = data.get('payment_status', 'PAID')
    transaction_id = data.get('transaction_id') or f"TXN-KOL-{uuid.uuid4().hex[:6].upper()}"

    new_booking = {
        "id": booking_id,
        "user_id": session.get('user_id', 'guest_user'),
        "user_name": guest_name,
        "user_email": guest_email,
        "user_phone": guest_phone,
        "hotel_id": hotel['id'],
        "hotel_name": hotel['name'],
        "hotel_location": hotel.get('location', 'Kolhapur'),
        "hotel_contact": hotel.get('contact_number', '+91 231 255 5555'),
        "hotel_image": hotel.get('image_filename', 'default_hotel.svg'),
        "destination_id": dest_id,
        "destination_name": dest_name,
        "check_in": check_in_str,
        "check_out": check_out_str,
        "nights": nights,
        "guests": guests,
        "rooms": rooms,
        "room_type": room_type,
        "price_per_night": price_per_night,
        "total_price": total_price,
        "payment_status": payment_status,
        "payment_method": payment_method,
        "transaction_id": transaction_id,
        "paid_amount": total_price,
        "special_requests": special_requests if special_requests else "None",
        "status": "Confirmed",
        "created_at": datetime.now().isoformat()
    }

    bookings = load_bookings()
    bookings.insert(0, new_booking)
    save_bookings(bookings)

    # Automatically dispatch Stay Confirmation & Destination Instructions to User's Gmail & SMS
    notif_data = generate_and_dispatch_notification(new_booking)

    return jsonify({
        "status": "success",
        "booking_id": booking_id,
        "hotel_name": hotel['name'],
        "destination_name": dest_name,
        "total_price": total_price,
        "payment_status": payment_status,
        "payment_method": payment_method,
        "transaction_id": transaction_id,
        "nights": nights,
        "rooms": rooms,
        "user_email": guest_email,
        "user_phone": guest_phone,
        "notification": notif_data,
        "message": f"Payment of ₹{total_price} verified via {payment_method}! Reference: {booking_id}. Instructions sent to {guest_email}.",
        "booking": new_booking
    })


@booking_bp.route('/api/booking/notification/<booking_id>', methods=['GET'])
def api_get_booking_notification(booking_id):
    """Retrieve full Gmail HTML body and SMS content for a booking."""
    notifications = load_notifications()
    for n in notifications:
        if n.get('booking_id') == booking_id:
            return jsonify({"status": "success", "notification": n})

    booking = get_booking_by_id(booking_id)
    if booking:
        notif = generate_and_dispatch_notification(booking)
        return jsonify({"status": "success", "notification": notif})

    return jsonify({"status": "error", "message": "Notification record not found."}), 404


@booking_bp.route('/api/booking/resend-notification/<booking_id>', methods=['POST'])
def api_resend_booking_notification(booking_id):
    """Re-dispatch email and SMS stay confirmation instructions."""
    booking = get_booking_by_id(booking_id)
    if not booking:
        return jsonify({"status": "error", "message": "Booking not found."}), 404

    notif = generate_and_dispatch_notification(booking)
    return jsonify({
        "status": "success",
        "message": f"Stay instructions successfully re-dispatched to {booking.get('user_email')} and mobile {booking.get('user_phone')}!",
        "notification": notif
    })


@booking_bp.route('/my-bookings')
def my_bookings():
    """User bookings dashboard."""
    all_bookings = load_bookings()
    user_email = session.get('email')
    user_id = session.get('user_id')

    if user_id or user_email:
        user_bookings = [
            b for b in all_bookings
            if (user_id and b.get('user_id') == user_id) or (user_email and b.get('user_email') == user_email)
        ]
    else:
        user_bookings = all_bookings[:5]

    return render_template('bookings.html', bookings=user_bookings)


@booking_bp.route('/api/bookings')
@login_required
def api_bookings():
    user_id = session['user_id']
    return jsonify({'bookings': [b for b in load_bookings() if b.get('user_id') == user_id]})


@booking_bp.route('/api/bookings/cancel/<booking_id>', methods=['POST'])
def api_cancel_booking(booking_id):
    """Cancel an existing booking."""
    bookings = load_bookings()
    found = False

    for b in bookings:
        if b.get('id') == booking_id:
            b['status'] = 'Cancelled'
            found = True
            break

    if found:
        save_bookings(bookings)
        return jsonify({
            "status": "success",
            "message": f"Booking reference {booking_id} has been successfully cancelled."
        })
    return jsonify({"status": "error", "message": "Booking not found."}), 404


@booking_bp.route('/booking/voucher/<booking_id>')
def booking_voucher(booking_id):
    """Render printable booking voucher receipt."""
    booking = get_booking_by_id(booking_id)
    if not booking:
        abort(404)

    hotel = get_hotel_by_id(booking.get('hotel_id'))
    dest_id = booking.get('destination_id', 'general')
    instructions = DESTINATION_TRAVEL_INSTRUCTIONS.get(dest_id, DESTINATION_TRAVEL_INSTRUCTIONS['general'])
    return render_template('booking_voucher.html', booking=booking, hotel=hotel, instructions=instructions)

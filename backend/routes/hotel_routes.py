from flask import Blueprint, render_template, request, jsonify, session
from backend.services.data_service import get_all_places, get_all_hotels, get_user_by_id
from backend.services.recommendation_service import recommend_hotels

hotel_bp = Blueprint('hotel_bp', __name__)


@hotel_bp.route('/hotels', methods=['GET', 'POST'])
@hotel_bp.route('/hotels/recommend', methods=['POST'], endpoint='hotels_recommend_post')
def hotels_page():
    """Interactive multi-criteria hotel recommendation page with live filters & booking modal."""
    if request.method == 'POST':
        dest_id = request.form.get('destination', 'mahalaxmi-temple')
        priority = request.form.get('priority', 'balanced')
        try:
            budget_min = int(request.form.get('budget_min', 500))
            budget_max = int(request.form.get('budget_max', 10000))
            min_rating = float(request.form.get('rating', 1.0))
        except (ValueError, TypeError):
            budget_min, budget_max, min_rating = 500, 10000, 1.0
        facilities = request.form.getlist('facilities')
    else:
        dest_id = request.args.get('destination', 'mahalaxmi-temple')
        priority = request.args.get('priority', 'balanced')
        try:
            budget_min = int(request.args.get('budget_min', 500))
            budget_max = int(request.args.get('budget_max', 10000))
            min_rating = float(request.args.get('rating', 1.0))
        except (ValueError, TypeError):
            budget_min, budget_max, min_rating = 500, 10000, 1.0
        facilities = request.args.getlist('facilities')

    recommended_hotels, target_place, stats = recommend_hotels(
        destination_id=dest_id,
        budget_min=budget_min,
        budget_max=budget_max,
        min_rating=min_rating,
        required_facilities=facilities,
        priority=priority
    )

    places = get_all_places()
    user_fav_hotels = []
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        if user and 'favorites' in user:
            user_fav_hotels = user['favorites'].get('hotels', [])

    return render_template(
        'hotels.html',
        hotels=recommended_hotels,
        places=places,
        selected_destination=dest_id,
        target_place=target_place,
        stats=stats,
        priority=priority,
        budget_min=budget_min,
        budget_max=budget_max,
        min_rating=min_rating,
        selected_facilities=facilities,
        user_favorite_hotels=user_fav_hotels
    )


@hotel_bp.route('/api/recommendations')
def api_recommendations():
    """JSON API returning scored hotels for asynchronous AJAX updates."""
    dest_id = request.args.get('destination')
    priority = request.args.get('priority', 'balanced')
    budget_min = int(request.args.get('budget_min', 500))
    budget_max = int(request.args.get('budget_max', 10000))
    min_rating = float(request.args.get('rating', 1.0))
    facilities = request.args.getlist('facilities')

    recommended, target_place, stats = recommend_hotels(
        destination_id=dest_id,
        budget_min=budget_min,
        budget_max=budget_max,
        min_rating=min_rating,
        required_facilities=facilities,
        priority=priority
    )

    return jsonify({
        "status": "success",
        "destination": target_place,
        "count": len(recommended),
        "stats": stats,
        "hotels": recommended
    })


@hotel_bp.route('/api/hotels')
def api_get_hotels():
    """JSON API to fetch all Kolhapur hotels."""
    return jsonify(get_all_hotels())

from flask import Blueprint, render_template, request, jsonify, abort, session
from backend.config import CATEGORIES
from backend.services.data_service import (
    get_all_places, get_all_hotels, get_place_by_id, get_hotel_by_id,
    get_user_by_id, update_user, login_required
)
from backend.services.recommendation_service import haversine_distance

tourism_bp = Blueprint('tourism_bp', __name__)


@tourism_bp.route('/')
def index():
    """Home page with hero search, voice triggers, category filters, and tourist cards."""
    places = get_all_places()
    user_fav_places = []
    user_fav_hotels = []

    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        if user and 'favorites' in user:
            user_fav_places = user['favorites'].get('places', [])
            user_fav_hotels = user['favorites'].get('hotels', [])

    return render_template(
        'index.html',
        places=places,
        categories=CATEGORIES,
        user_favorite_places=user_fav_places,
        user_favorite_hotels=user_fav_hotels
    )


@tourism_bp.route('/place/<place_id>')
def place_detail(place_id):
    """Detailed heritage view of a tourist place with nearby scored stays."""
    place = get_place_by_id(place_id)
    if not place:
        abort(404)

    hotels = get_all_hotels()
    nearby_hotels = []
    for h in hotels:
        h_copy = dict(h)
        h_copy['distance_km'] = haversine_distance(
            place['latitude'], place['longitude'],
            h['latitude'], h['longitude']
        )
        h_copy['directions_url'] = f"https://www.google.com/maps/dir/?api=1&origin={place['latitude']},{place['longitude']}&destination={h['latitude']},{h['longitude']}"
        nearby_hotels.append(h_copy)

    nearby_hotels.sort(key=lambda x: x['distance_km'])
    top_nearby = nearby_hotels[:4]

    is_fav = False
    if 'user_id' in session:
        user = get_user_by_id(session['user_id'])
        if user and 'favorites' in user:
            is_fav = place_id in user['favorites'].get('places', [])

    return render_template(
        'place_detail.html',
        place=place,
        nearby_hotels=top_nearby,
        is_favorite=is_fav
    )


@tourism_bp.route('/about')
def about():
    """Project overview, data science documentation, and viva summary."""
    places = get_all_places()
    hotels = get_all_hotels()
    return render_template(
        'about.html',
        total_places=len(places),
        total_hotels=len(hotels)
    )


@tourism_bp.route('/my-favorites')
@login_required
def my_favorites():
    """User favorites page."""
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return render_template('login.html')

    fav_place_ids = user.get('favorites', {}).get('places', [])
    fav_hotel_ids = user.get('favorites', {}).get('hotels', [])

    fav_places = [get_place_by_id(pid) for pid in fav_place_ids if get_place_by_id(pid)]
    fav_hotels = [get_hotel_by_id(hid) for hid in fav_hotel_ids if get_hotel_by_id(hid)]

    return render_template(
        'favorites.html',
        favorite_places=fav_places,
        favorite_hotels=fav_hotels,
        user=user
    )


@tourism_bp.route('/api/favorites/toggle', methods=['POST'])
def api_toggle_favorite():
    """Toggle a place or hotel in user's saved favorites."""
    if 'user_id' not in session:
        return jsonify({
            "status": "unauthorized",
            "message": "Please log in to save items to your favorites."
        }), 401

    data = request.get_json() or {}
    item_id = data.get('item_id')
    item_type = data.get('item_type')  # 'place' or 'hotel'

    if not item_id or item_type not in ['place', 'hotel']:
        return jsonify({"status": "error", "message": "Invalid request parameters."}), 400

    user = get_user_by_id(session['user_id'])
    if not user:
        return jsonify({"status": "error", "message": "User not found."}), 404

    if 'favorites' not in user:
        user['favorites'] = {"places": [], "hotels": []}

    target_list = user['favorites']['places'] if item_type == 'place' else user['favorites']['hotels']

    if item_id in target_list:
        target_list.remove(item_id)
        action = "removed"
    else:
        target_list.append(item_id)
        action = "added"

    update_user(user)

    return jsonify({
        "status": "success",
        "action": action,
        "item_id": item_id,
        "item_type": item_type,
        "total_favorites": len(target_list)
    })


@tourism_bp.route('/api/places')
def api_get_places():
    """JSON API to fetch all tourist attractions."""
    return jsonify(get_all_places())


@tourism_bp.route('/search')
def search():
    """Universal destination search route."""
    query = request.args.get('q', '').lower().strip()
    category = request.args.get('category', 'all').lower().strip()
    places = get_all_places()

    results = []
    for p in places:
        name = p.get('name', '').lower()
        desc = p.get('description', '').lower()
        cat = p.get('category', '').lower()

        matches_cat = (category == 'all' or cat == category)
        matches_query = (not query or query in name or query in desc or query in cat)

        if matches_cat and matches_query:
            results.append(p)

    return render_template(
        'index.html',
        places=results,
        categories=CATEGORIES,
        search_query=query,
        active_category=category,
        user_favorite_places=[]
    )

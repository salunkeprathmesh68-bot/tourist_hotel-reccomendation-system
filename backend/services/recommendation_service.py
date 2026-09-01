import math
from backend.services.data_service import get_all_hotels, get_place_by_id


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great-circle distance between two geographical coordinates on Earth
    using the Haversine Formula.
    
    Formula:
        a = sin²(Δlat/2) + cos(lat1) * cos(lat2) * sin²(Δlon/2)
        c = 2 * atan2(√a, √(1−a))
        d = R * c  (where R = 6371.0 km Earth radius)
    """
    R = 6371.0  # Earth's mean radius in kilometers

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))

    distance_km = R * c
    return round(distance_km, 2)


def recommend_hotels(destination_id=None, budget_min=500, budget_max=10000,
                     min_rating=1.0, required_facilities=None, priority="balanced"):
    """
    Multi-criteria hotel recommendation algorithm for Kolhapur tourism.
    
    Algorithm Weights:
    - Balanced : Distance 40%, Rating 30%, Price 20%, Amenities 10%
    - Proximity: Distance 65%, Rating 15%, Price 10%, Amenities 10%
    - Budget   : Price 60%, Distance 20%, Rating 15%, Amenities 5%
    - Rating   : Rating 60%, Distance 20%, Price 15%, Amenities 5%
    """
    hotels = get_all_hotels()
    if not hotels:
        return [], None, {}

    target_place = None
    if destination_id:
        target_place = get_place_by_id(destination_id)

    # If no valid destination, default to central Kolhapur (Mahalaxmi Temple coords)
    if target_place:
        dest_lat = target_place['latitude']
        dest_lon = target_place['longitude']
    else:
        dest_lat = 16.6946
        dest_lon = 74.2238

    if required_facilities is None:
        required_facilities = []

    # Filter candidate hotels
    filtered_hotels = []
    for h in hotels:
        price = h.get('price_per_night', 0)
        rating = h.get('rating', 0.0)
        facilities = h.get('facilities', [])

        if price < budget_min or price > budget_max:
            continue
        if rating < min_rating:
            continue

        # Check required facilities
        if required_facilities:
            has_all_facilities = all(req.lower() in [f.lower() for f in facilities] for req in required_facilities)
            if not has_all_facilities:
                continue

        h_copy = dict(h)
        h_copy['distance_km'] = haversine_distance(
            dest_lat, dest_lon, h['latitude'], h['longitude']
        )
        filtered_hotels.append(h_copy)

    if not filtered_hotels:
        return [], target_place, {"total_evaluated": len(hotels), "matching_criteria": 0}

    # Normalize metrics for multi-criteria scoring
    distances = [h['distance_km'] for h in filtered_hotels]
    prices = [h['price_per_night'] for h in filtered_hotels]
    ratings = [h['rating'] for h in filtered_hotels]

    min_dist, max_dist = min(distances), max(distances)
    min_price, max_price = min(prices), max(prices)
    min_rat, max_rat = min(ratings), max(ratings)

    # Set priority weights
    if priority == "proximity":
        w_dist, w_rat, w_price, w_fac = 0.65, 0.15, 0.10, 0.10
    elif priority == "budget":
        w_dist, w_rat, w_price, w_fac = 0.20, 0.15, 0.60, 0.05
    elif priority == "rating":
        w_dist, w_rat, w_price, w_fac = 0.20, 0.60, 0.15, 0.05
    else:  # balanced
        w_dist, w_rat, w_price, w_fac = 0.40, 0.30, 0.20, 0.10

    for h in filtered_hotels:
        # Distance score (lower distance = higher score)
        if max_dist > min_dist:
            dist_score = 1.0 - ((h['distance_km'] - min_dist) / (max_dist - min_dist))
        else:
            dist_score = 1.0

        # Price score (lower price = higher score)
        if max_price > min_price:
            price_score = 1.0 - ((h['price_per_night'] - min_price) / (max_price - min_price))
        else:
            price_score = 1.0

        # Rating score (higher rating = higher score)
        if max_rat > min_rat:
            rating_score = (h['rating'] - min_rat) / (max_rat - min_rat)
        else:
            rating_score = 1.0 if h['rating'] >= 4.0 else 0.5

        # Facility count score
        fac_count = len(h.get('facilities', []))
        facility_score = min(fac_count / 8.0, 1.0)

        # Composite multi-criteria final score (0 - 100)
        composite = (w_dist * dist_score +
                     w_rat * rating_score +
                     w_price * price_score +
                     w_fac * facility_score) * 100.0

        h['recommendation_score'] = round(composite, 1)
        h['score_breakdown'] = {
            "proximity_score": round(dist_score * 100, 1),
            "rating_score": round(rating_score * 100, 1),
            "budget_score": round(price_score * 100, 1),
            "amenity_score": round(facility_score * 100, 1)
        }

        # Google Maps directions URL
        h['directions_url'] = f"https://www.google.com/maps/dir/?api=1&origin={dest_lat},{dest_lon}&destination={h['latitude']},{h['longitude']}"

    # Sort descending by recommendation score
    filtered_hotels.sort(key=lambda x: x['recommendation_score'], reverse=True)

    stats = {
        "total_evaluated": len(hotels),
        "matching_criteria": len(filtered_hotels),
        "min_distance": min(distances) if distances else 0,
        "max_distance": max(distances) if distances else 0
    }

    return filtered_hotels, target_place, stats

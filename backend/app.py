import os
from flask import Flask, render_template, url_for
from backend.config import (
    SECRET_KEY, TEMPLATE_DIR, STATIC_DIR, CATEGORIES
)
from backend.services.data_service import get_all_places, get_all_hotels
from backend.routes.auth_routes import auth_bp
from backend.routes.tourism_routes import tourism_bp
from backend.routes.hotel_routes import hotel_bp
from backend.routes.booking_routes import booking_bp


def create_app():
    """Application factory for Smart Kolhapur Guide."""
    app = Flask(
        __name__,
        template_folder=TEMPLATE_DIR,
        static_folder=STATIC_DIR,
        static_url_path='/static'
    )

    app.config['SECRET_KEY'] = SECRET_KEY

    # Register modular Blueprints
    app.register_blueprint(tourism_bp)
    app.register_blueprint(hotel_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(auth_bp)

    # Register root aliases for un-prefixed url_for calls in templates
    endpoint_map = {
        'index': 'tourism_bp.index',
        'place_detail': 'tourism_bp.place_detail',
        'about': 'tourism_bp.about',
        'my_favorites': 'tourism_bp.my_favorites',
        'search': 'tourism_bp.search',
        'hotels_page': 'hotel_bp.hotels_page',
        'hotels_recommend_post': 'hotel_bp.hotels_recommend_post',
        'my_bookings': 'booking_bp.my_bookings',
        'booking_voucher': 'booking_bp.booking_voucher',
        'login': 'auth_bp.login',
        'signup': 'auth_bp.signup',
        'logout': 'auth_bp.logout',
        'forgot_password': 'auth_bp.forgot_password'
    }

    for rule in list(app.url_map.iter_rules()):
        for short_ep, full_ep in endpoint_map.items():
            if rule.endpoint == full_ep:
                try:
                    app.add_url_rule(
                        rule.rule,
                        endpoint=short_ep,
                        view_func=app.view_functions[full_ep],
                        methods=rule.methods
                    )
                except Exception:
                    pass

    # Template Context Processor
    @app.context_processor
    def inject_global_context():
        return {
            'all_categories': CATEGORIES,
            'total_places_count': len(get_all_places()),
            'total_hotels_count': len(get_all_hotels())
        }

    # Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('500.html'), 500

    return app


# Default application instance
app = create_app()

if __name__ == '__main__':
    print("============================================================")
    print(" [START] SMART KOLHAPUR GUIDE - Modular Backend Starting")
    print(" [INFO]  District: Kolhapur, Maharashtra, India")
    print(f" [INFO]  Templates: {TEMPLATE_DIR}")
    print(f" [INFO]  Static Assets: {STATIC_DIR}")
    print(" [INFO]  Running on: http://127.0.0.1:5000")
    print("============================================================")
    app.run(debug=True, host='127.0.0.1', port=5000)

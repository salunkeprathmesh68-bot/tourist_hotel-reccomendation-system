import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from backend.services.data_service import (
    load_users, save_users, get_user_by_email, update_user
)

auth_bp = Blueprint('auth_bp', __name__)


def public_user(user):
    """Return the account shape used by the React client without the hash."""
    favorites = user.get('favorites', {})
    if not favorites:
        favorites = {
            'places': user.get('favorites_places', []),
            'hotels': user.get('favorites_hotels', [])
        }
    return {k: v for k, v in {**user, 'favorites': favorites}.items() if k != 'password_hash'}


@auth_bp.route('/api/auth/me')
def api_me():
    user = load_users()
    current = next((item for item in user if item.get('id') == session.get('user_id')), None)
    return jsonify({'user': public_user(current) if current else None})


@auth_bp.route('/api/auth/login', methods=['POST'])
def api_login():
    data = request.get_json(silent=True) or {}
    account = get_user_by_email(data.get('email', ''))
    if not account or not check_password_hash(account.get('password_hash', ''), data.get('password', '')):
        return jsonify({'message': 'Email or password is incorrect.'}), 401
    session.update(user_id=account['id'], name=account['name'], email=account['email'], role=account.get('role', 'tourist'))
    return jsonify({'user': public_user(account)})


@auth_bp.route('/api/auth/signup', methods=['POST'])
def api_signup():
    data = request.get_json(silent=True) or {}
    name, email, password = data.get('name', '').strip(), data.get('email', '').strip().lower(), data.get('password', '')
    if not name or not email or len(password) < 6 or password != data.get('confirm_password'):
        return jsonify({'message': 'Enter a name, valid email, and matching password of at least 6 characters.'}), 400
    if get_user_by_email(email):
        return jsonify({'message': 'An account with this email already exists.'}), 409
    account = {'id': f"user_{uuid.uuid4().hex[:8]}", 'name': name, 'email': email, 'phone': data.get('phone', ''), 'password_hash': generate_password_hash(password), 'role': 'tourist', 'favorites': {'places': [], 'hotels': []}, 'created_at': datetime.now().isoformat()}
    users = load_users()
    users.append(account)
    if not save_users(users):
        return jsonify({'message': 'Unable to create the account right now.'}), 500
    session.update(user_id=account['id'], name=name, email=email, role='tourist')
    return jsonify({'user': public_user(account)}), 201


@auth_bp.route('/api/auth/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'status': 'success'})


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login portal."""
    if 'user_id' in session:
        return redirect(url_for('tourism_bp.index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash("Please provide both email and password.", "danger")
            return render_template('login.html', email=email)

        user = get_user_by_email(email)
        if not user or not check_password_hash(user.get('password_hash', ''), password):
            flash("Invalid email or password. Please check your credentials.", "danger")
            return render_template('login.html', email=email)

        # Set session
        session['user_id'] = user['id']
        session['name'] = user['name']
        session['email'] = user['email']
        session['role'] = user.get('role', 'tourist')

        flash(f"Welcome back, {user['name']}! Explore Kolhapur's best attractions.", "success")
        next_page = request.args.get('next')
        if next_page and next_page.startswith('/'):
            return redirect(next_page)
        return redirect(url_for('tourism_bp.index'))

    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """New user registration."""
    if 'user_id' in session:
        return redirect(url_for('tourism_bp.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not name or not email or not password:
            flash("Name, email, and password are required fields.", "danger")
            return render_template('signup.html', name=name, email=email, phone=phone)

        if len(password) < 6:
            flash("Password must be at least 6 characters long.", "warning")
            return render_template('signup.html', name=name, email=email, phone=phone)

        if password != confirm_password:
            flash("Passwords do not match. Please verify and retype.", "danger")
            return render_template('signup.html', name=name, email=email, phone=phone)

        if get_user_by_email(email):
            flash("An account with this email address already exists. Please sign in.", "warning")
            return redirect(url_for('auth_bp.login', email=email))

        user_id = f"user_{uuid.uuid4().hex[:8]}"
        password_hash = generate_password_hash(password)

        new_user = {
            "id": user_id,
            "name": name,
            "email": email,
            "phone": phone if phone else "+91 98765 43210",
            "password_hash": password_hash,
            "role": "tourist",
            "favorites": {
                "places": ["mahalaxmi-temple", "panhala-fort"],
                "hotels": ["hotel-ambience-kolhapur"]
            },
            "created_at": datetime.now().isoformat()
        }

        users = load_users()
        users.append(new_user)
        save_users(users)

        session['user_id'] = new_user['id']
        session['name'] = new_user['name']
        session['email'] = new_user['email']
        session['role'] = new_user['role']

        flash(f"Account created successfully! Welcome to Kolhapur Guide, {name}!", "success")
        return redirect(url_for('tourism_bp.index'))

    return render_template('signup.html')


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Dedicated forgot password / reset flow."""
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if not email or not new_password or not confirm_password:
            flash("All fields are required to reset your password.", "danger")
            return render_template('forgot_password.html', email=email)

        if len(new_password) < 6:
            flash("New password must be at least 6 characters long.", "warning")
            return render_template('forgot_password.html', email=email)

        if new_password != confirm_password:
            flash("Passwords do not match. Please confirm your new password carefully.", "danger")
            return render_template('forgot_password.html', email=email)

        user = get_user_by_email(email)
        if not user:
            flash("No registered account found with that email address. Please register a new account.", "danger")
            return render_template('forgot_password.html', email=email)

        user['password_hash'] = generate_password_hash(new_password)
        update_user(user)

        flash("Your password has been successfully reset! You can now log in with your new password.", "success")
        return redirect(url_for('auth_bp.login', email=email))

    return render_template('forgot_password.html')


@auth_bp.route('/logout')
def logout():
    """Log out current user."""
    name = session.get('name', 'Traveler')
    session.clear()
    flash(f"You have been signed out. Thank you for visiting Kolhapur Guide, {name}!", "info")
    return redirect(url_for('tourism_bp.index'))

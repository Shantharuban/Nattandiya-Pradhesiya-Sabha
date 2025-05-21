from flask import Blueprint, request, jsonify, render_template_string, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

import models # Import models directly
from extensions import db # Import db from extensions.py

# Using Blueprint to organize routes
# Authentication routes
auth_bp = Blueprint('auth', __name__)
# Main application routes (including protected ones)
main_bp = Blueprint('main', __name__)

# --- Authentication Routes ---

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard')) # Redirect if already logged in

    if request.method == 'POST':
        data = request.get_json()
        if not data:
            # Fallback for form data if JSON is not sent
            username = request.form.get('username')
            password = request.form.get('password')
        else:
            username = data.get('username')
            password = data.get('password')

        if not username or not password:
            flash('Username and password are required.', 'danger')
            if request.is_json:
                return jsonify({"message": "Username and password are required."}), 400
            # For non-JSON, re-render a simple login form (or redirect to a GET login page)
            return render_template_string(LOGIN_FORM_TEMPLATE, error="Username and password are required."), 400


        user = models.User.query.filter_by(username=username).first()

        if user and user.check_password(password):
            login_user(user, remember=True) # 'remember=True' can be configurable
            flash('Logged in successfully!', 'success')
            
            next_page = request.args.get('next')
            if request.is_json:
                return jsonify({"message": "Login successful", "next": next_page or url_for('main.dashboard')}), 200
            return redirect(next_page or url_for('main.dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            if request.is_json:
                return jsonify({"message": "Invalid username or password"}), 401
            return render_template_string(LOGIN_FORM_TEMPLATE, error="Invalid username or password."), 401

    # For GET request, show a simple login form
    return render_template_string(LOGIN_FORM_TEMPLATE)

@auth_bp.route('/logout')
@login_required # Ensures only logged-in users can logout
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    if request.is_json:
        return jsonify({"message": "Logout successful"}), 200
    return redirect(url_for('auth.login'))

# --- Main Application Routes (Protected) ---

@main_bp.route('/')
@main_bp.route('/dashboard')
@login_required # Protect this route
def dashboard():
    if request.is_json:
        return jsonify(message=f"Welcome to the Admin Dashboard, {current_user.username}! Your role is {current_user.role}.")
    return render_template_string(DASHBOARD_TEMPLATE, user=current_user)
    
@main_bp.route('/admin/create_user', methods=['POST'])
@login_required
def create_user_route():
    if not current_user.role == 'admin':
        if request.is_json:
            return jsonify({"message": "Forbidden: Admins only"}), 403
        flash("Forbidden: Admins only", "danger")
        return redirect(url_for('main.dashboard'))

    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    role = data.get('role', 'editor') # Default role is 'editor'

    if not username or not password:
        return jsonify({"message": "Username and password are required"}), 400
    
    if models.User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists"}), 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = models.User(username=username, hashed_password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": f"User {username} created successfully with role {role}"}), 201


# --- HTML Templates (for simplicity, in a real app these would be in separate .html files) ---

LOGIN_FORM_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Login</title>
    <style>
        body { font-family: sans-serif; margin: 20px; background-color: #f4f4f4; }
        .container { background-color: #fff; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h2 { text-align: center; color: #333; }
        label { display: block; margin-bottom: 5px; color: #555; }
        input[type="text"], input[type="password"] {
            width: calc(100% - 22px); padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 3px;
        }
        button {
            background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 3px; cursor: pointer; width: 100%;
        }
        button:hover { background-color: #0056b3; }
        .flash {
            padding: 10px; margin-bottom: 15px; border-radius: 3px;
            color: #fff;
        }
        .flash.danger { background-color: #dc3545; }
        .flash.success { background-color: #28a745; }
        .flash.info { background-color: #17a2b8; }
        .error { color: red; margin-bottom: 10px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Admin Panel Login</h2>
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {% if error %}
            <p class="error">{{ error }}</p>
        {% endif %}
        <form method="POST" action="{{ url_for('auth.login') }}">
            <div>
                <label for="username">Username:</label>
                <input type="text" id="username" name="username" required>
            </div>
            <div>
                <label for="password">Password:</label>
                <input type="password" id="password" name="password" required>
            </div>
            <button type="submit">Login</button>
        </form>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Admin Dashboard</title>
     <style>
        body { font-family: sans-serif; margin: 0; background-color: #f4f4f4; display: flex; flex-direction: column; min-height: 100vh; }
        .navbar { background-color: #333; padding: 10px 20px; color: white; display: flex; justify-content: space-between; align-items: center; }
        .navbar a { color: white; text-decoration: none; padding: 8px 15px; }
        .navbar a:hover { background-color: #555; border-radius: 3px; }
        .container { flex-grow: 1; padding: 20px; }
        .content { background-color: #fff; padding: 20px; border-radius: 5px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        h1 { color: #333; }
        .flash {
            padding: 10px; margin-bottom: 15px; border-radius: 3px;
            color: #fff;
        }
        .flash.danger { background-color: #dc3545; }
        .flash.success { background-color: #28a745; }
        .flash.info { background-color: #17a2b8; }
    </style>
</head>
<body>
    <div class="navbar">
        <div>Admin Panel</div>
        <div>
            <a href="{{ url_for('council_info.edit_council_info') }}">Council Info</a>
            <a href="{{ url_for('members.list_members') }}">Members</a>
            <a href="{{ url_for('divisions_committees.list_divisions_committees') }}">Divisions/Committees</a>
            <a href="{{ url_for('news.list_news_events') }}" style="margin-left: 15px;">News & Events</a>
            <a href="{{ url_for('documents.list_documents') }}">Documents</a>
            <a href="{{ url_for('services.list_services') }}">Services</a>
            <span style="margin-left: 20px;">Welcome, {{ user.username }} ({{user.role}})!</span>
            <a href="{{ url_for('auth.logout') }}" style="margin-left: 10px;">Logout</a>
        </div>
    </div>
    <div class="container">
         {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash {{ category }}">{{ message }}</li>
                {% endfor %}
            {% endif %}
        {% endwith %}
        <div class="content">
            <h1>Admin Dashboard</h1>
            <p>This is a protected area. Use the links above to navigate to different management sections.</p>
            <!-- Add more dashboard content here -->
        </div>
    </div>
</body>
</html>
"""

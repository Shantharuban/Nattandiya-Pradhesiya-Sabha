from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user, login_required

def admin_required(func):
    """
    Decorator to ensure the current user is logged in and has the 'admin' role.
    Redirects to the main dashboard with a flash message if not authorized.
    """
    @wraps(func)
    @login_required # Ensures user is logged in first
    def decorated_view(*args, **kwargs):
        if not hasattr(current_user, 'role') or current_user.role != 'admin':
            flash('This action requires admin privileges.', 'danger')
            # Redirect to a general page, e.g., main dashboard or login,
            # as the 'news.list_news_events' might not be universally appropriate.
            # Using 'main.dashboard' as a more generic admin-accessible page.
            return redirect(url_for('main.dashboard')) 
        return func(*args, **kwargs)
    return decorated_view

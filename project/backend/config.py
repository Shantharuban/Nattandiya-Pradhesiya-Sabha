import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_very_secret_key_here' # Change this in production!
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True # Set to False in production
    # For Flask-Login
    LOGIN_VIEW = 'auth.login' # The name of the login view function
    USE_SESSION_FOR_NEXT = True
    REMEMBER_COOKIE_DURATION = 86400 # 1 day in seconds
    REMEMBER_COOKIE_SECURE = False # Set to True in production if using HTTPS
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False # Set to True in production if using HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax' # Can be 'Strict', 'Lax', or 'None'

    # File Upload Configuration
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads', 'documents')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx'}


# To generate a good secret key, you can use:
# import secrets
# secrets.token_hex(16)

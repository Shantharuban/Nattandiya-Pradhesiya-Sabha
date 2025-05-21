import os
from flask import Flask
from werkzeug.security import generate_password_hash
import os

# Import extensions from extensions.py
from extensions import db, login_manager

def create_app():
    """Create and configure an instance of the Flask application."""
    # Define paths for frontend templates and static files relative to this file's location (project/backend/app.py)
    # Project root is one level up from app.py's directory
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    frontend_template_folder = os.path.join(project_root, 'frontend', 'templates')
    frontend_static_folder = os.path.join(project_root, 'frontend', 'static')

    app = Flask(
        __name__,
        instance_relative_config=True,
        template_folder=frontend_template_folder, # Primary template folder for the app
        static_folder=frontend_static_folder # Primary static folder for the app
    )
    # Note: Blueprints can also have their own template_folder and static_folder,
    # which are usually relative to the blueprint's location.
    # The main app's template_folder will be searched if a template isn't found
    # in a blueprint's specific template_folder.
    # For admin templates, they are in project/backend/templates/admin, so we need to ensure
    # Flask also looks there. Default Flask behavior with blueprints might handle this if blueprints
    # specify their template_folder correctly, or we might need a ChoiceLoader.

    # Load configuration
    app.config.from_object('config.Config')

    # Ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
        print(f"Instance folder created at {app.instance_path}")
    except OSError:
        pass # Already exists
    
    # Create upload folder if it doesn't exist
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'])
        print(f"Upload folder created at {app.config['UPLOAD_FOLDER']}")
    except OSError:
        pass # Already exists or error creating

    # Initialize extensions with the app
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # The route for login (name of the view function)
    login_manager.login_message_category = "info" # Flash message category

    # Import models here, after db is initialized and within app context for operations
    # Models need db to be defined at import time for class definitions.
    # Routes need models and db.
    import models # This will now import db from extensions.py

    with app.app_context():
        # The user_loader is defined in models.py using login_manager from extensions.py
        
        # Create database tables if they don't exist
        # This needs to be done after models are defined and db is initialized.
        db.create_all()
        print("Database tables checked/created.")

        # Check if the admin user exists, if not create one
        if models.User.query.filter_by(username='admin').first() is None:
            print("Admin user not found, creating one...")
            hashed_password = generate_password_hash('adminpassword', method='pbkdf2:sha256')
            admin_user = models.User(username='admin', hashed_password=hashed_password, role='admin')
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user 'admin' with password 'adminpassword' created.")
        else:
            print("Admin user already exists.")

    # Import and register blueprints
    # Blueprints might import models and db, so do this after db.init_app and models import
    import routes
    from news_routes import news_bp
    from document_routes import documents_bp
    from services_routes import services_bp
    from council_info_routes import council_info_bp
    from members_routes import members_bp
    from divisions_committees_routes import divisions_committees_bp
    
    app.register_blueprint(routes.auth_bp, url_prefix='/auth')
    app.register_blueprint(routes.main_bp) # For dashboard and other main routes
    app.register_blueprint(news_bp) 
    app.register_blueprint(documents_bp) 
    app.register_blueprint(services_bp)
    app.register_blueprint(council_info_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(divisions_committees_bp)

    # Register Frontend Blueprint
    from frontend_routes import frontend_bp # Import the frontend blueprint
    app.register_blueprint(frontend_bp)


    return app

# The user_loader callback needs to be accessible to login_manager.
# It's usually defined in models.py or where the User model is.
# We'll ensure it's correctly loaded from models.py

# if __name__ == '__main__':
#     # To run with python app.py, you might need to add the project directory to PYTHONPATH
#     # or run as a module: python -m project.backend.app
#     # For development, it's common to use `flask run` command.
#     # Set FLASK_APP=project.backend.app (or just app.py if in the backend folder)
#     # Set FLASK_ENV=development (or FLASK_DEBUG=1)
#     # Example:
#     # export FLASK_APP=app.py
#     # export FLASK_DEBUG=1
#     # flask run
if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=app.config['DEBUG'])

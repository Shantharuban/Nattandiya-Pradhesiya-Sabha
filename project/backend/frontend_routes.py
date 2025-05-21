from flask import Blueprint, render_template, current_app
from models import CouncilInfo, NewsAndEvents, Services # Assuming models are in models.py
from extensions import db # If direct db session usage is needed, though typically through models

# Define the blueprint. 
# The template_folder is relative to the blueprint's location if not absolute.
# Since this blueprint is in project/backend, and templates are in project/frontend/templates/public:
# We can rely on the app's ChoiceLoader configured in app.py to find 'public/index.html'
# from the 'project/frontend/templates/' path.
# Similarly for static files, the app's static_folder is set to project/frontend/static.
# If this blueprint had its own static files, we'd set static_folder here.
frontend_bp = Blueprint(
    'frontend', 
    __name__,
    # template_folder='../../frontend/templates', # Not strictly needed if app's jinja_loader is correctly configured
    # static_folder='../../frontend/static' # Not strictly needed if app's static_folder is correctly configured
)

@frontend_bp.route('/')
def homepage():
    # Fetch CouncilInfo - assuming there's only one entry or we take the first
    council_info = CouncilInfo.query.first() 

    # Fetch 3-5 most recent News items
    # Assuming 'type' field in NewsAndEvents distinguishes news from events
    recent_news = NewsAndEvents.query.filter_by(type='news')\
                                     .order_by(NewsAndEvents.date.desc(), NewsAndEvents.created_at.desc())\
                                     .limit(5).all()
    
    # Fetch some services for Quick Links (e.g., first 5 services)
    # This is a placeholder; specific logic for which services to show might be needed
    quick_link_services = Services.query.order_by(Services.name.asc()).limit(5).all()

    # Render the public homepage template
    # The template path 'public/index.html' will be resolved by the ChoiceLoader
    # to look inside 'project/frontend/templates/public/index.html'.
    return render_template(
        'public/index.html', 
        council_info=council_info, 
        recent_news=recent_news,
        quick_link_services=quick_link_services
    )

@frontend_bp.route('/about-us')
def about_us_page():
    # Fetch CouncilInfo data
    council_info = CouncilInfo.query.first()

    # Fetch all Members, ordered by display_order, then by name
    members = Members.query.order_by(Members.display_order.asc(), Members.name.asc()).all()

    # Render the public about_us.html template
    # The template path 'public/about.html' will be resolved by the ChoiceLoader
    return render_template(
        'public/about.html',
        council_info=council_info,
        members=members
    )

@frontend_bp.route('/services')
def services_list_page():
    # Fetch all Services, ordered by name
    all_services = Services.query.order_by(Services.name.asc()).all()
    return render_template(
        'public/services_list.html',
        services=all_services
    )

@frontend_bp.route('/services/<int:service_id>', methods=['GET', 'POST'])
def service_detail_page(service_id):
    service = Services.query.get_or_404(service_id)

    if request.method == 'POST':
        if service.type and service.type.lower() == 'form_based':
            user_name = request.form.get('user_name')
            user_contact = request.form.get('user_contact')
            submission_content = request.form.get('submission_content')

            if not all([user_name, user_contact, submission_content]):
                flash('All form fields are required for submission.', 'danger')
                # Re-render form with current service data but no form data (or pass submitted data back if desired)
                return render_template('public/service_detail.html', service=service)

            new_submission = ServiceSubmissions(
                service_id=service.id,
                user_name=user_name,
                user_contact=user_contact,
                submission_content=submission_content,
                status='Pending' # Default status
                # last_updated_by_id can be null for public submissions initially
            )
            db.session.add(new_submission)
            try:
                db.session.commit()
                flash('Your request has been submitted successfully! We will get back to you soon.', 'success')
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(f"Error saving submission: {e}")
                flash('There was an error submitting your request. Please try again later.', 'danger')
            
            return redirect(url_for('frontend.service_detail_page', service_id=service.id))
        else:
            # POST request to a non-form_based service or service without type; should not happen with current HTML
            flash('This service does not accept submissions via this method.', 'warning')
            return redirect(url_for('frontend.service_detail_page', service_id=service.id))

    # For GET request
    return render_template('public/service_detail.html', service=service)

@frontend_bp.route('/divisions-and-committees')
def divisions_committees_page():
    all_items = DivisionsAndCommittees.query.order_by(DivisionsAndCommittees.name.asc()).all()
    divisions = [item for item in all_items if item.type == 'division']
    committees = [item for item in all_items if item.type == 'committee']
    return render_template(
        'public/divisions_committees.html',
        divisions=divisions,
        committees=committees
    )

# Example of how to serve a static file from this blueprint if it had its own static dir
# @frontend_bp.route('/robots.txt')
# def static_from_root():
#     return send_from_directory(current_app.static_folder, request.path[1:])
# Note: This is usually handled by Flask's default static file serving if static_folder is set on app or blueprint.
# For CSS, JS, images, direct linking in HTML <link href="{{ url_for('static', filename='css/style.css') }}"> works
# if app.static_folder points to project/frontend/static.

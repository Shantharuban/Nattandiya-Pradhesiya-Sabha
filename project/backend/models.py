from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from extensions import db, login_manager # Import db and login_manager from extensions.py

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    hashed_password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), nullable=False, default='editor') # e.g., 'admin', 'editor'
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

@login_manager.user_loader
def load_user(user_id):
    """User loader function for Flask-Login."""
    return User.query.get(int(user_id))


class NewsAndEvents(db.Model):
    __tablename__ = 'news_and_events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # 'news' or 'event'
    image_url = db.Column(db.String(255), nullable=True)
    video_url = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    last_updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    
    # Foreign Key to User table for tracking who created/updated
    # Assuming 'editor' role and above can manage news/events
    # last_updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    # last_updated_by_user = db.relationship('User', backref=db.backref('news_events_updates', lazy='dynamic'))
    
    # For simplicity, we might not add last_updated_by_id yet if not strictly required by initial CRUD
    # It's in the schema, so good to have:
    last_updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    last_updated_by_user = db.relationship('User', backref='news_events_log')


    def __repr__(self):
        return f'<NewsAndEvents {self.id}: {self.title}>'

class Documents(db.Model):
    __tablename__ = 'documents'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    # Stores the path relative to the UPLOAD_FOLDER or a full URL if external
    file_path_or_url = db.Column(db.String(255), nullable=False) 
    category = db.Column(db.String(100), nullable=True) # e.g., form, notice, budget
    publication_date = db.Column(db.Date, nullable=True)
    
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    last_updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    
    uploader_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploader = db.relationship('User', backref=db.backref('uploaded_documents', lazy='dynamic'))

    def __repr__(self):
        return f'<Documents {self.id}: {self.title}>'

class Services(db.Model):
    __tablename__ = 'services'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(100), nullable=True) # e.g., 'informational', 'form_based'
    
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    last_updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    
    # Renamed from last_updated_by to created_by_id as per task, assuming last_updated_by_id is also needed for consistency
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False) 
    creator = db.relationship('User', backref=db.backref('created_services', lazy='dynamic'))

    submissions = db.relationship('ServiceSubmissions', backref='service', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<Services {self.id}: {self.name}>'

class ServiceSubmissions(db.Model):
    __tablename__ = 'service_submissions'

    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False)
    
    # For user_details, using separate columns as per common practice, though JSON could be an option
    user_name = db.Column(db.String(255), nullable=False)
    user_contact = db.Column(db.String(255), nullable=False) # Could be email or phone
    
    submission_content = db.Column(db.Text, nullable=True) # For form-based services, this could be JSON string or detailed text
    status = db.Column(db.String(50), nullable=False, default='pending') # e.g., pending, approved, rejected
    submission_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    remarks = db.Column(db.Text, nullable=True) # Admin remarks on the submission
    
    # last_updated_by links to Users table for admin who last touched this submission
    last_updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    last_updated_by_user = db.relationship('User', backref='updated_service_submissions')
    last_updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)


    def __repr__(self):
        return f'<ServiceSubmissions {self.id} for Service {self.service_id}>'

class CouncilInfo(db.Model):
    __tablename__ = 'council_info'

    id = db.Column(db.Integer, primary_key=True) # Should only be one row with id=1 ideally
    introduction = db.Column(db.Text, nullable=True)
    mission = db.Column(db.Text, nullable=True)
    history = db.Column(db.Text, nullable=True)
    vision = db.Column(db.Text, nullable=True)
    goals = db.Column(db.Text, nullable=True) # Could be stored as JSON or delimited text if multiple goals

    last_updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    last_updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    last_updated_by_user = db.relationship('User', backref='council_info_updates')

    def __repr__(self):
        return f'<CouncilInfo {self.id}>'

class Members(db.Model):
    __tablename__ = 'members'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(255), nullable=True) # External URL for image
    display_order = db.Column(db.Integer, nullable=True, default=0) # For ordering members

    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    last_updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)
    
    # Using last_updated_by_id for consistency with other models, implies who last edited this member.
    # If 'created_by_id' is strictly needed, it can be added and only set on creation.
    last_updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    last_updated_by_user = db.relationship('User', backref='member_updates')

    def __repr__(self):
        return f'<Members {self.id}: {self.name}>'

class DivisionsAndCommittees(db.Model):
    __tablename__ = 'divisions_and_committees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=False) # 'division' or 'committee'

    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    last_updated_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False)

    # Using last_updated_by_id for consistency.
    last_updated_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    last_updated_by_user = db.relationship('User', backref='division_committee_updates')

    def __repr__(self):
        return f'<DivisionsAndCommittees {self.id}: {self.name} ({self.type})>'


# You can add other models here as the application grows, for example:
# class ContentTranslations(db.Model):
# # ...

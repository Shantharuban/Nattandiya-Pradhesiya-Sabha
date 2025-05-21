from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user

from extensions import db
from models import Services, ServiceSubmissions # Assuming these models are in models.py
from utils import admin_required # Importing admin_required decorator

services_bp = Blueprint('services', __name__, template_folder='templates')

# --- Service Definition CRUD ---

@services_bp.route('/admin/services')
@admin_required
def list_services():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    services_pagination = Services.query.order_by(Services.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    svcs = services_pagination.items
    return render_template('admin/services_list.html', services=svcs, pagination=services_pagination, current_user=current_user)

@services_bp.route('/admin/services/create', methods=['GET', 'POST'])
@admin_required
def create_service():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        service_type = request.form.get('type')

        if not name:
            flash('Service name is required.', 'danger')
            return render_template('admin/service_form.html', service=request.form, current_user=current_user)

        new_service = Services(
            name=name,
            description=description,
            type=service_type,
            created_by_id=current_user.id
        )
        db.session.add(new_service)
        db.session.commit()
        flash('Service created successfully!', 'success')
        return redirect(url_for('services.list_services'))

    return render_template('admin/service_form.html', service=None, current_user=current_user)

@services_bp.route('/admin/services/edit/<int:service_id>', methods=['GET', 'POST'])
@admin_required
def edit_service(service_id):
    service = Services.query.get_or_404(service_id)
    if request.method == 'POST':
        service.name = request.form.get('name')
        service.description = request.form.get('description')
        service.type = request.form.get('type')
        
        if not service.name:
            flash('Service name is required.', 'danger')
            return render_template('admin/service_form.html', service=service, current_user=current_user)

        # Update who last modified it - assuming we add a last_updated_by_id to Services model
        # For now, created_by_id remains the original creator. last_updated_at will auto-update.
        
        db.session.commit()
        flash('Service updated successfully!', 'success')
        return redirect(url_for('services.list_services'))

    return render_template('admin/service_form.html', service=service, current_user=current_user)

@services_bp.route('/admin/services/delete/<int:service_id>', methods=['POST'])
@admin_required
def delete_service(service_id):
    service = Services.query.get_or_404(service_id)
    # ServiceSubmissions associated with this service will be deleted due to cascade="all, delete-orphan"
    db.session.delete(service)
    db.session.commit()
    flash('Service and all its submissions deleted successfully!', 'success')
    return redirect(url_for('services.list_services'))

# --- Service Submission Viewing & Management ---

@services_bp.route('/admin/services/submissions/<int:service_id>')
@admin_required
def list_service_submissions(service_id):
    service = Services.query.get_or_404(service_id)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    submissions_pagination = ServiceSubmissions.query.filter_by(service_id=service_id)\
                               .order_by(ServiceSubmissions.submission_date.desc())\
                               .paginate(page=page, per_page=per_page, error_out=False)
    submissions = submissions_pagination.items
    return render_template('admin/service_submissions_list.html', submissions=submissions, service=service, pagination=submissions_pagination, current_user=current_user)

@services_bp.route('/admin/services/submission/<int:submission_id>')
@admin_required
def view_submission(submission_id):
    submission = ServiceSubmissions.query.get_or_404(submission_id)
    return render_template('admin/submission_detail.html', submission=submission, current_user=current_user)

@services_bp.route('/admin/services/submission/<int:submission_id>/update_status', methods=['POST'])
@admin_required
def update_submission_status(submission_id):
    submission = ServiceSubmissions.query.get_or_404(submission_id)
    new_status = request.form.get('status')
    remarks = request.form.get('remarks')

    allowed_statuses = ['pending', 'approved', 'rejected', 'in_progress', 'completed']
    if new_status not in allowed_statuses:
        flash(f'Invalid status: {new_status}.', 'danger')
        return redirect(url_for('services.view_submission', submission_id=submission_id))

    submission.status = new_status
    submission.remarks = remarks
    submission.last_updated_by_id = current_user.id
    # submission.last_updated_at will auto-update via model definition
    
    db.session.commit()
    flash(f'Submission ID {submission.id} status updated to {new_status}.', 'success')
    return redirect(url_for('services.view_submission', submission_id=submission_id))

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from datetime import datetime

from extensions import db
from models import Documents # Assuming Documents model is in models.py
from utils import admin_required # Importing admin_required decorator

documents_bp = Blueprint('documents', __name__, template_folder='templates')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

@documents_bp.route('/admin/documents')
@admin_required
def list_documents():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    documents_pagination = Documents.query.order_by(Documents.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    docs = documents_pagination.items
    return render_template('admin/documents_list.html', documents=docs, pagination=documents_pagination, current_user=current_user)

@documents_bp.route('/admin/documents/upload', methods=['GET', 'POST'])
@admin_required
def upload_document():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        publication_date_str = request.form.get('publication_date')
        
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)

        if not title:
            flash('Title is required.', 'danger')
            # Consider re-rendering form with other filled data
            return render_template('admin/document_form.html', document=None, current_user=current_user)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # To avoid overwrites and create unique filenames, append a timestamp or UUID
            # For simplicity here, we'll just use the secure_filename directly but this is not robust for production
            # A better approach: filename = str(uuid.uuid4()) + "_" + secure_filename(file.filename)
            
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder) # Ensure it exists, though app.py should handle it
            
            file_path = os.path.join(upload_folder, filename)
            
            # Check for filename collision (simple check, might need more robust handling)
            if os.path.exists(file_path):
                flash(f'File with name {filename} already exists. Please rename or upload a different file.', 'danger')
                return render_template('admin/document_form.html', document=request.form, current_user=current_user)

            file.save(file_path)

            publication_date_obj = None
            if publication_date_str:
                try:
                    publication_date_obj = datetime.strptime(publication_date_str, '%Y-%m-%d').date()
                except ValueError:
                    flash('Invalid publication date format. Please use YYYY-MM-DD.', 'danger')
                    # Clean up saved file if date is invalid and required, or handle as partial success
                    os.remove(file_path) # Example cleanup
                    return render_template('admin/document_form.html', document=request.form, current_user=current_user)

            new_document = Documents(
                title=title,
                description=description,
                file_path_or_url=filename, # Store only filename, path is derived from UPLOAD_FOLDER
                category=category,
                publication_date=publication_date_obj,
                uploader_id=current_user.id
            )
            db.session.add(new_document)
            db.session.commit()
            flash('Document uploaded successfully!', 'success')
            return redirect(url_for('documents.list_documents'))
        else:
            flash('File type not allowed.', 'danger')
            return redirect(request.url)

    return render_template('admin/document_form.html', document=None, current_user=current_user)

@documents_bp.route('/admin/documents/edit/<int:doc_id>', methods=['GET', 'POST'])
@admin_required
def edit_document(doc_id):
    doc = Documents.query.get_or_404(doc_id)
    if request.method == 'POST':
        doc.title = request.form.get('title')
        doc.description = request.form.get('description')
        doc.category = request.form.get('category')
        publication_date_str = request.form.get('publication_date')

        if not doc.title:
            flash('Title is required.', 'danger')
            return render_template('admin/document_form.html', document=doc, current_user=current_user)

        if publication_date_str:
            try:
                doc.publication_date = datetime.strptime(publication_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid publication date format. Use YYYY-MM-DD.', 'danger')
                return render_template('admin/document_form.html', document=doc, current_user=current_user)
        else:
            doc.publication_date = None

        # File replacement logic (optional for this version, as per instructions)
        if 'file' in request.files:
            new_file = request.files['file']
            if new_file and new_file.filename != '' and allowed_file(new_file.filename):
                # Delete old file
                old_file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.file_path_or_url)
                if os.path.exists(old_file_path):
                    try:
                        os.remove(old_file_path)
                    except OSError as e:
                        flash(f"Error deleting old file: {e}", "danger")
                
                # Save new file
                filename = secure_filename(new_file.filename)
                new_file.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
                doc.file_path_or_url = filename # Update filename in DB
            elif new_file.filename != '': # File selected but type not allowed
                 flash('New file type not allowed. File was not replaced.', 'danger')


        doc.uploader_id = current_user.id # Or keep original uploader? For now, last editor.
        # last_updated_at is handled by model's onupdate

        db.session.commit()
        flash('Document updated successfully!', 'success')
        return redirect(url_for('documents.list_documents'))

    return render_template('admin/document_form.html', document=doc, current_user=current_user)

@documents_bp.route('/admin/documents/delete/<int:doc_id>', methods=['POST'])
@admin_required
def delete_document(doc_id):
    doc = Documents.query.get_or_404(doc_id)
    try:
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], doc.file_path_or_url)
        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            flash(f"File not found at {file_path}. Record deleted anayway.", "warning")

        db.session.delete(doc)
        db.session.commit()
        flash('Document and associated file deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting document: {str(e)}', 'danger')
    return redirect(url_for('documents.list_documents'))

@documents_bp.route('/admin/documents/download/<int:doc_id>')
@login_required # Or @admin_required depending on policy
def download_document(doc_id):
    doc = Documents.query.get_or_404(doc_id)
    try:
        return send_from_directory(current_app.config['UPLOAD_FOLDER'], doc.file_path_or_url, as_attachment=True)
    except FileNotFoundError:
        flash('File not found.', 'danger')
        return redirect(url_for('documents.list_documents'))

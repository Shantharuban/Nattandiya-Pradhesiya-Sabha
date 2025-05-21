from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user

from extensions import db
from models import CouncilInfo 
from utils import admin_required

council_info_bp = Blueprint('council_info', __name__, template_folder='templates')

COUNCIL_INFO_ID = 1 # Assuming CouncilInfo has a single row with ID 1

@council_info_bp.route('/admin/council_info/edit', methods=['GET', 'POST'])
@admin_required
def edit_council_info():
    # Try to get the existing council info, or create a new one if it doesn't exist
    council_info_entry = CouncilInfo.query.get(COUNCIL_INFO_ID)
    if not council_info_entry:
        council_info_entry = CouncilInfo(id=COUNCIL_INFO_ID) # Initialize with default ID
        db.session.add(council_info_entry)
        # Commit immediately if creating, or defer until after form processing
        # For simplicity, we can commit here or let the post handler do it.
        # If we don't commit, and the user just GETs the page without POSTing, 
        # the entry won't be in DB for the template if it relies on it being there.
        # However, the template should handle `council_info` being None or new.
        # Let's assume template handles it gracefully or we pass a new object.
        # For this form, it's better if the object exists for the template to read from.
        try:
            db.session.commit()
            council_info_entry = CouncilInfo.query.get(COUNCIL_INFO_ID) # Re-fetch
        except Exception as e:
            db.session.rollback()
            flash(f"Error initializing council info: {e}", "danger")
            return redirect(url_for('main.dashboard')) # Or some error page


    if request.method == 'POST':
        council_info_entry.introduction = request.form.get('introduction')
        council_info_entry.mission = request.form.get('mission')
        council_info_entry.history = request.form.get('history')
        council_info_entry.vision = request.form.get('vision')
        council_info_entry.goals = request.form.get('goals')
        council_info_entry.last_updated_by_id = current_user.id
        
        try:
            db.session.commit()
            flash('Council information updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating council information: {str(e)}', 'danger')
        
        return redirect(url_for('council_info.edit_council_info'))

    return render_template('admin/council_info_form.html', council_info=council_info_entry, current_user=current_user)

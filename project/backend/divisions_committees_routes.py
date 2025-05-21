from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user

from extensions import db
from models import DivisionsAndCommittees
from utils import admin_required

divisions_committees_bp = Blueprint('divisions_committees', __name__, template_folder='templates')

@divisions_committees_bp.route('/admin/divisions_committees')
@admin_required
def list_divisions_committees():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    # Order by type, then by name
    items_pagination = DivisionsAndCommittees.query.order_by(DivisionsAndCommittees.type.asc(), DivisionsAndCommittees.name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    items = items_pagination.items
    return render_template('admin/divisions_committees_list.html', items=items, pagination=items_pagination, current_user=current_user)

@divisions_committees_bp.route('/admin/divisions_committees/create', methods=['GET', 'POST'])
@admin_required
def create_division_committee():
    if request.method == 'POST':
        name = request.form.get('name')
        item_type = request.form.get('type')
        description = request.form.get('description')

        if not name or not item_type:
            flash('Name and type are required.', 'danger')
            return render_template('admin/division_committee_form.html', item=request.form, current_user=current_user)
        
        if item_type not in ['division', 'committee']:
            flash('Invalid type selected.', 'danger')
            return render_template('admin/division_committee_form.html', item=request.form, current_user=current_user)

        new_item = DivisionsAndCommittees(
            name=name,
            type=item_type,
            description=description,
            last_updated_by_id=current_user.id # Tracks who created/last updated
        )
        db.session.add(new_item)
        db.session.commit()
        flash(f'{item_type.capitalize()} created successfully!', 'success')
        return redirect(url_for('divisions_committees.list_divisions_committees'))

    return render_template('admin/division_committee_form.html', item=None, current_user=current_user)

@divisions_committees_bp.route('/admin/divisions_committees/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required
def edit_division_committee(item_id):
    item = DivisionsAndCommittees.query.get_or_404(item_id)
    if request.method == 'POST':
        item.name = request.form.get('name')
        item.type = request.form.get('type')
        item.description = request.form.get('description')
        
        if not item.name or not item.type:
            flash('Name and type are required.', 'danger')
            return render_template('admin/division_committee_form.html', item=item, current_user=current_user)

        if item.type not in ['division', 'committee']:
            flash('Invalid type selected.', 'danger')
            return render_template('admin/division_committee_form.html', item=item, current_user=current_user)
            
        item.last_updated_by_id = current_user.id
        
        db.session.commit()
        flash(f'{item.type.capitalize()} updated successfully!', 'success')
        return redirect(url_for('divisions_committees.list_divisions_committees'))

    return render_template('admin/division_committee_form.html', item=item, current_user=current_user)

@divisions_committees_bp.route('/admin/divisions_committees/delete/<int:item_id>', methods=['POST'])
@admin_required
def delete_division_committee(item_id):
    item = DivisionsAndCommittees.query.get_or_404(item_id)
    item_type_str = item.type.capitalize()
    db.session.delete(item)
    db.session.commit()
    flash(f'{item_type_str} deleted successfully!', 'success')
    return redirect(url_for('divisions_committees.list_divisions_committees'))

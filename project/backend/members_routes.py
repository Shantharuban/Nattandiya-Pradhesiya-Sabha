from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import current_user

from extensions import db
from models import Members
from utils import admin_required

members_bp = Blueprint('members', __name__, template_folder='templates')

@members_bp.route('/admin/members')
@admin_required
def list_members():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    # Order by display_order, then by name
    members_pagination = Members.query.order_by(Members.display_order.asc(), Members.name.asc()).paginate(page=page, per_page=per_page, error_out=False)
    mems = members_pagination.items
    return render_template('admin/members_list.html', members=mems, pagination=members_pagination, current_user=current_user)

@members_bp.route('/admin/members/create', methods=['GET', 'POST'])
@admin_required
def create_member():
    if request.method == 'POST':
        name = request.form.get('name')
        role = request.form.get('role')
        bio = request.form.get('bio')
        image_url = request.form.get('image_url')
        display_order_str = request.form.get('display_order')

        if not name:
            flash('Member name is required.', 'danger')
            return render_template('admin/member_form.html', member=request.form, current_user=current_user)
        
        display_order = 0
        if display_order_str:
            try:
                display_order = int(display_order_str)
            except ValueError:
                flash('Invalid display order. Must be a number.', 'danger')
                return render_template('admin/member_form.html', member=request.form, current_user=current_user)


        new_member = Members(
            name=name,
            role=role,
            bio=bio,
            image_url=image_url if image_url else None,
            display_order=display_order,
            last_updated_by_id=current_user.id # Tracks who created/last updated
        )
        db.session.add(new_member)
        db.session.commit()
        flash('Member added successfully!', 'success')
        return redirect(url_for('members.list_members'))

    return render_template('admin/member_form.html', member=None, current_user=current_user)

@members_bp.route('/admin/members/edit/<int:member_id>', methods=['GET', 'POST'])
@admin_required
def edit_member(member_id):
    member = Members.query.get_or_404(member_id)
    if request.method == 'POST':
        member.name = request.form.get('name')
        member.role = request.form.get('role')
        member.bio = request.form.get('bio')
        member.image_url = request.form.get('image_url')
        display_order_str = request.form.get('display_order')
        
        if not member.name:
            flash('Member name is required.', 'danger')
            return render_template('admin/member_form.html', member=member, current_user=current_user)

        if display_order_str:
            try:
                member.display_order = int(display_order_str)
            except ValueError:
                flash('Invalid display order. Must be a number.', 'danger')
                return render_template('admin/member_form.html', member=member, current_user=current_user)
        else:
            member.display_order = 0
            
        member.last_updated_by_id = current_user.id
        
        db.session.commit()
        flash('Member updated successfully!', 'success')
        return redirect(url_for('members.list_members'))

    return render_template('admin/member_form.html', member=member, current_user=current_user)

@members_bp.route('/admin/members/delete/<int:member_id>', methods=['POST'])
@admin_required
def delete_member(member_id):
    member = Members.query.get_or_404(member_id)
    db.session.delete(member)
    db.session.commit()
    flash('Member deleted successfully!', 'success')
    return redirect(url_for('members.list_members'))

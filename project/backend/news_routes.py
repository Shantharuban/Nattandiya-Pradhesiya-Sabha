from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from datetime import datetime
# functools.wraps is now used within the admin_required decorator in utils.py

from extensions import db
from models import NewsAndEvents # Assuming NewsAndEvents model is in models.py
from utils import admin_required # Import admin_required from utils.py

news_bp = Blueprint('news', __name__, template_folder='templates')

# admin_required decorator is now imported from utils

@news_bp.route('/admin/news_events')
@login_required # Basic login check, admin check can be added if needed for viewing by non-admins
def list_news_events():
    page = request.args.get('page', 1, type=int)
    per_page = 10 # Or from config
    items_pagination = NewsAndEvents.query.order_by(NewsAndEvents.date.desc(), NewsAndEvents.last_updated_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    items = items_pagination.items
    return render_template('admin/news_events_list.html', items=items, pagination=items_pagination, current_user=current_user)

@news_bp.route('/admin/news_events/create', methods=['GET', 'POST'])
@admin_required # Ensure only admins can create
def create_news_event():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        date_str = request.form.get('date')
        item_type = request.form.get('type')
        image_url = request.form.get('image_url')
        video_url = request.form.get('video_url')

        if not all([title, content, date_str, item_type]):
            flash('Title, content, date, and type are required.', 'danger')
            # Optionally, re-render form with existing data
            return render_template('admin/news_events_form.html', item=request.form, current_user=current_user)
        
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('admin/news_events_form.html', item=request.form, current_user=current_user)

        new_item = NewsAndEvents(
            title=title,
            content=content,
            date=date_obj,
            type=item_type,
            image_url=image_url if image_url else None,
            video_url=video_url if video_url else None,
            last_updated_by_id=current_user.id
        )
        db.session.add(new_item)
        db.session.commit()
        flash('News/Event item created successfully!', 'success')
        return redirect(url_for('news.list_news_events'))

    return render_template('admin/news_events_form.html', item=None, current_user=current_user) # Pass item=None for create form

@news_bp.route('/admin/news_events/edit/<int:item_id>', methods=['GET', 'POST'])
@admin_required # Ensure only admins can edit
def edit_news_event(item_id):
    item = NewsAndEvents.query.get_or_404(item_id)

    if request.method == 'POST':
        item.title = request.form.get('title')
        item.content = request.form.get('content')
        date_str = request.form.get('date')
        item.type = request.form.get('type')
        item.image_url = request.form.get('image_url')
        item.video_url = request.form.get('video_url')

        if not all([item.title, item.content, date_str, item.type]):
            flash('Title, content, date, and type are required.', 'danger')
            return render_template('admin/news_events_form.html', item=item, current_user=current_user)

        try:
            item.date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD.', 'danger')
            return render_template('admin/news_events_form.html', item=item, current_user=current_user)
        
        item.last_updated_by_id = current_user.id
        # last_updated_at is handled by server_default/onupdate in model

        db.session.commit()
        flash('News/Event item updated successfully!', 'success')
        return redirect(url_for('news.list_news_events'))

    return render_template('admin/news_events_form.html', item=item, current_user=current_user)

@news_bp.route('/admin/news_events/delete/<int:item_id>', methods=['POST']) # POST for safety
@admin_required # Ensure only admins can delete
def delete_news_event(item_id):
    item = NewsAndEvents.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('News/Event item deleted successfully!', 'success')
    return redirect(url_for('news.list_news_events'))

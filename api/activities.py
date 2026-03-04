import csv
import io
import logging
import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, Response
from backend.activities import get_activities, create_activity, delete_activity
from backend.locations import get_or_create_location
from backend.auth import get_all_usernames

logger = logging.getLogger(__name__)

activities_bp = Blueprint('activities', __name__)

PER_PAGE = 20


@activities_bp.route('/')
def index():
    filter_address = request.args.get('filter_address', '').strip()
    filter_date_from = request.args.get('filter_date_from', '').strip()
    filter_date_to = request.args.get('filter_date_to', '').strip()
    filter_usernames = request.args.getlist('filter_usernames')
    page = int(request.args.get('page', 1))

    activities, total = get_activities(
        filter_address=filter_address or None,
        filter_date_from=filter_date_from or None,
        filter_date_to=filter_date_to or None,
        filter_usernames=filter_usernames or None,
        page=page,
        per_page=PER_PAGE
    )

    total_pages = max(1, (total + PER_PAGE - 1) // PER_PAGE)

    template_vars = dict(
        activities=activities,
        page=page,
        total_pages=total_pages,
        filter_address=filter_address,
        filter_date_from=filter_date_from,
        filter_date_to=filter_date_to,
        filter_usernames=filter_usernames,
    )

    if request.args.get('partial') == '1':
        return render_template('_table.html', **template_vars)

    return render_template(
        'index.html',
        **template_vars,
        all_usernames=get_all_usernames(),
        geoapify_api_key=os.getenv('GEOAPIFY_API_KEY', '')
    )


@activities_bp.route('/activities', methods=['POST'])
def create():
    address = request.form.get('address', '').strip()
    note = request.form.get('note', '').strip()

    if not all([address, note]):
        flash('Address and note are required.', 'error')
        return redirect(url_for('activities.index'))

    location_id = get_or_create_location(address)
    user_id = session.get('user_id', 1)

    create_activity(location_id=location_id, user_id=user_id, note=note)

    logger.info("User '%s' created activity at '%s'", session.get('username'), address)
    flash('Activity saved.', 'success')
    return redirect(url_for('activities.index'))


@activities_bp.route('/activities/<int:activity_id>/delete', methods=['POST'])
def delete(activity_id):
    delete_activity(activity_id)
    logger.info("User '%s' deleted activity id=%d", session.get('username'), activity_id)
    flash('Activity deleted.', 'success')
    return redirect(url_for('activities.index'))


@activities_bp.route('/activities/export')
def export():
    filter_address = request.args.get('filter_address', '').strip()
    filter_date_from = request.args.get('filter_date_from', '').strip()
    filter_date_to = request.args.get('filter_date_to', '').strip()
    filter_usernames = request.args.getlist('filter_usernames')

    activities, _ = get_activities(
        filter_address=filter_address or None,
        filter_date_from=filter_date_from or None,
        filter_date_to=filter_date_to or None,
        filter_usernames=filter_usernames or None,
        page=1,
        per_page=100_000
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Date & Time', 'Address', 'Note', 'Logged By'])
    for a in activities:
        writer.writerow([a['activity_date'], a['address'], a['note'], a['username']])

    output.seek(0)
    return Response(
        output,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=activities.csv'}
    )

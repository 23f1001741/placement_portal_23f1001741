from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.models import db, User, CompanyProfile, PlacementDrive, Application
from cache import cache

admin_bp = Blueprint('admin', __name__)

def is_admin():
    claims = get_jwt()
    return claims.get('role') == 'admin'

@admin_bp.route('/dashboard', methods=['GET'])
@jwt_required()
def admin_dashboard():
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403

    total_students = User.query.filter_by(role='student').count()
    total_companies = CompanyProfile.query.count()
    total_drives = PlacementDrive.query.count()

    return jsonify({
        "total_students": total_students,
        "total_companies": total_companies,
        "total_drives": total_drives
    }), 200

@admin_bp.route('/companies/pending', methods=['GET'])
@jwt_required()
def get_pending_companies():
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403
        
    pending = CompanyProfile.query.filter_by(approval_status='Pending').all()
    result = [{
        "id": c.id, 
        "name": c.company_name, 
        "hr_contact": c.hr_contact,
        "website": c.website
    } for c in pending]
    
    return jsonify(result), 200

@admin_bp.route('/companies/<int:company_id>/status', methods=['POST'])
@jwt_required()
def update_company_status(company_id):
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403
        
    company = CompanyProfile.query.get_or_404(company_id)
    data = request.get_json()
    action = data.get('action')
    
    if action in ['Approved', 'Rejected']:
        company.approval_status = action
        db.session.commit()
        cache.clear() # Clear cache so students see new companies
        return jsonify({"message": f"Company {action.lower()} successfully"}), 200
        
    return jsonify({"message": "Invalid action. Use 'Approved' or 'Rejected'"}), 400

@admin_bp.route('/drives/pending', methods=['GET'])
@jwt_required()
def get_pending_drives():
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403
        
    pending_drives = db.session.query(PlacementDrive, CompanyProfile).join(
        CompanyProfile, PlacementDrive.company_id == CompanyProfile.id
    ).filter(PlacementDrive.status == 'Pending').all()
    
    result = [{
        "id": drive.id,
        "company_name": company.company_name,
        "job_title": drive.job_title,
        "deadline": drive.application_deadline.strftime('%Y-%m-%d')
    } for drive, company in pending_drives]
    
    return jsonify(result), 200

@admin_bp.route('/drives/<int:drive_id>/status', methods=['POST'])
@jwt_required()
def update_drive_status(drive_id):
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403
        
    drive = PlacementDrive.query.get_or_404(drive_id)
    data = request.get_json()
    action = data.get('action')
    
    if action in ['Approved', 'Rejected']:
        drive.status = action
        db.session.commit()
        cache.clear() # Clear cache so students see the approved drive [cite: 5]
        return jsonify({"message": f"Drive {action.lower()} successfully"}), 200
        
    return jsonify({"message": "Invalid action. Use 'Approved' or 'Rejected'"}), 400

@admin_bp.route('/drives', methods=['GET'])
@jwt_required()
def get_global_drives():
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403

    search_term = request.args.get('search', '')
    query = db.session.query(PlacementDrive, CompanyProfile).join(
        CompanyProfile, PlacementDrive.company_id == CompanyProfile.id
    )

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(db.or_(
            PlacementDrive.job_title.ilike(search_pattern),
            CompanyProfile.company_name.ilike(search_pattern)
        ))

    drives = query.all()
    return jsonify([{
        "id": d.id,
        "company_name": c.company_name,
        "job_title": d.job_title,
        "status": d.status
    } for d, c in drives]), 200

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_all_users():
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403

    search_term = request.args.get('search', '')
    query = User.query.filter(User.role != 'admin')

    if search_term:
        search_pattern = f"%{search_term}%"
        query = query.filter(
            db.or_(
                User.username.ilike(search_pattern),
                User.email.ilike(search_pattern)
            )
        )

    users = query.all()
    result = [{
        "id": u.id,
        "username": u.username,
        "email": u.email,
        "role": u.role,
        "is_active": u.active
    } for u in users]

    return jsonify(result), 200

@admin_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@jwt_required()
def toggle_user_status(user_id):
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403
    
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        return jsonify({"message": "Cannot deactivate Admin"}), 400

    user.active = not user.active 
    db.session.commit()
    
    status = "activated" if user.active else "deactivated"
    return jsonify({"message": f"User {status} successfully"}), 200

@admin_bp.route('/placement-stats', methods=['GET'])
@jwt_required()
def get_placement_stats():
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403

    stats = {
        "applied": Application.query.filter_by(status='Applied').count(),
        "shortlisted": Application.query.filter_by(status='Shortlisted').count(),
        "interviewed": Application.query.filter_by(status='Interview Scheduled').count(),
        "selected": Application.query.filter_by(status='Selected').count(),
        "rejected": Application.query.filter_by(status='Rejected').count()
    }
    return jsonify(stats), 200

@admin_bp.route('/interviews', methods=['GET'])
@jwt_required()
def get_global_interviews():
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403

    interviews = db.session.query(Application, User, PlacementDrive, CompanyProfile).join(
        User, Application.student_id == User.id
    ).join(
        PlacementDrive, Application.drive_id == PlacementDrive.id
    ).join(
        CompanyProfile, PlacementDrive.company_id == CompanyProfile.id
    ).filter(Application.status == 'Interview Scheduled').all()

    result = [{
        "id": app.id,
        "interview_date": app.interview_date,
        "student_name": user.username,
        "company_name": comp.company_name,
        "job_title": drive.job_title
    } for app, user, drive, comp in interviews]

    return jsonify(result), 200

@admin_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_all_applications():
    if not is_admin():
        return jsonify({"message": "Admin access required"}), 403

    apps = db.session.query(Application, User, PlacementDrive, CompanyProfile).join(
        User, Application.student_id == User.id
    ).join(
        PlacementDrive, Application.drive_id == PlacementDrive.id
    ).join(
        CompanyProfile, PlacementDrive.company_id == CompanyProfile.id
    ).all()

    return jsonify([{
        "id": app.id,
        "student_name": user.username,
        "job_title": drive.job_title,
        "company_name": company.company_name,
        "applied_on": app.application_date.strftime('%Y-%m-%d'),
        "status": app.status
    } for app, user, drive, company in apps]), 200
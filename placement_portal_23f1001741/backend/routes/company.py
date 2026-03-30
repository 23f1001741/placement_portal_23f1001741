from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.models import db, CompanyProfile, PlacementDrive, User, Application, StudentProfile
from datetime import datetime
from tasks import export_csv_task, send_interview_notification
from cache import cache

company_bp = Blueprint('company', __name__)

def is_company():
    claims = get_jwt()
    return claims.get('role') == 'company'

@company_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_company_stats():
    if not is_company():
        return jsonify({"message": "Company access required"}), 403

    user_id = int(get_jwt_identity())
    company = CompanyProfile.query.filter_by(user_id=user_id).first()
    if not company:
        return jsonify({"message": "Profile not found"}), 404

    total_drives = PlacementDrive.query.filter_by(company_id=company.id).count()
    total_applicants = db.session.query(Application).join(
        PlacementDrive, Application.drive_id == PlacementDrive.id
    ).filter(PlacementDrive.company_id == company.id).count()

    return jsonify({
        "company_name": company.company_name,
        "approval_status": company.approval_status,
        "total_drives": total_drives,
        "total_applicants": total_applicants
    }), 200

@company_bp.route('/drives', methods=['POST'])
@jwt_required()
def create_drive():
    if not is_company():
        return jsonify({"message": "Company access required"}), 403

    company = CompanyProfile.query.filter_by(user_id=int(get_jwt_identity())).first()
    if company.approval_status != 'Approved':
        return jsonify({"message": "Company must be approved by Admin"}), 403

    data = request.get_json()
    try:
        deadline = datetime.strptime(data.get('application_deadline'), '%Y-%m-%d')
        new_drive = PlacementDrive(
            company_id=company.id,
            job_title=data.get('job_title'),
            job_description=data.get('job_description'),
            eligibility_criteria=data.get('eligibility_criteria'),
            minimum_cgpa=float(data.get('minimum_cgpa', 0.0)),
            application_deadline=deadline,
            status='Pending'
        )
        db.session.add(new_drive)
        db.session.commit()
        cache.clear()
        return jsonify({"message": "Drive created! Pending approval."}), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 400

@company_bp.route('/drives', methods=['GET'])
@jwt_required()
def get_company_drives():
    if not is_company():
        return jsonify({"message": "Company access required"}), 403
    company = CompanyProfile.query.filter_by(user_id=int(get_jwt_identity())).first()
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    return jsonify([{"id": d.id, "job_title": d.job_title, "status": d.status, "deadline": d.application_deadline.strftime('%Y-%m-%d')} for d in drives]), 200

@company_bp.route('/drives/<int:drive_id>/applications', methods=['GET'])
@jwt_required()
def get_drive_applications(drive_id):
    if not is_company():
        return jsonify({"message": "Company access required"}), 403
    
    apps = Application.query.filter_by(drive_id=drive_id).all()
    result = []
    for app in apps:
        student = User.query.get(app.student_id)
        profile = StudentProfile.query.filter_by(user_id=app.student_id).first()
        result.append({
            "id": app.id,
            "student_name": student.username,
            "student_email": student.email,
            "status": app.status,
            "interview_date": app.interview_date,
            "resume_url": profile.resume_url if profile else None
        })
    return jsonify(result), 200

@company_bp.route('/applications/<int:app_id>/status', methods=['PUT'])
@jwt_required()
def update_application_status(app_id):
    if not is_company():
        return jsonify({"message": "Company access required"}), 403
    app = Application.query.get_or_404(app_id)
    app.status = request.json.get('status')
    db.session.commit()
    return jsonify({"message": "Status updated"}), 200

@company_bp.route('/applications/<int:app_id>/schedule', methods=['POST'])
@jwt_required()
def schedule_interview(app_id):
    if not is_company():
        return jsonify({"message": "Company access required"}), 403
    app = Application.query.get_or_404(app_id)
    drive = PlacementDrive.query.get(app.drive_id)
    date_val = request.json.get('date')
    app.status = "Interview Scheduled"
    app.interview_date = date_val
    db.session.commit()
    student = User.query.get(app.student_id)
    send_interview_notification.delay(student.email, drive.job_title, date_val)
    return jsonify({"message": "Interview scheduled"}), 200

@company_bp.route('/drives/<int:drive_id>/export', methods=['POST'])
@jwt_required()
def export_drive_applications(drive_id):
    if not is_company():
        return jsonify({"message": "Company access required"}), 403
    user = User.query.get(get_jwt_identity())
    export_csv_task.delay(drive_id, user.email)
    return jsonify({"message": "Export started! Check MailHog."}), 202

@company_bp.route('/drives/<int:drive_id>/close', methods=['POST'])
@jwt_required()
def close_placement_drive(drive_id):
    if not is_company():
        return jsonify({"message": "Company access required"}), 403
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = 'Closed'
    db.session.commit()
    cache.clear()
    return jsonify({"message": "Drive closed"}), 200
import os
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.models import db, User, PlacementDrive, Application, CompanyProfile, StudentProfile
from cache import cache
from werkzeug.utils import secure_filename
from tasks import export_student_applications_task 

student_bp = Blueprint('student', __name__)

UPLOAD_FOLDER = 'uploads/resumes'
ALLOWED_EXTENSIONS = {'pdf'}

def is_student():
    claims = get_jwt()
    return claims.get('role') == 'student'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@student_bp.route('/drives', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, query_string=True)
def get_approved_drives():
    if not is_student():
        return jsonify({"message": "Student access required"}), 403
    
    search_term = request.args.get('search', '')
    
    query = db.session.query(PlacementDrive, CompanyProfile).join(
        CompanyProfile, PlacementDrive.company_id == CompanyProfile.id
    ).filter(PlacementDrive.status == 'Approved')
    
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
        "job_description": d.job_description,
        "eligibility_criteria": d.eligibility_criteria,
        "minimum_cgpa": d.minimum_cgpa,
        "deadline": d.application_deadline.strftime('%Y-%m-%d')
    } for d, c in drives]), 200

@student_bp.route('/applications', methods=['POST'])
@jwt_required()
def apply_for_drive():
    if not is_student():
        return jsonify({"message": "Student access required"}), 403

    user_id = int(get_jwt_identity())
    data = request.get_json()
    drive_id = data.get('drive_id')

    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.status != 'Approved':
        return jsonify({"message": "Drive is no longer active"}), 400

    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    if not profile or profile.cgpa < drive.minimum_cgpa:
        return jsonify({"message": f"Ineligible. Your CGPA ({profile.cgpa if profile else 0}) is below {drive.minimum_cgpa}"}), 403

    if Application.query.filter_by(student_id=user_id, drive_id=drive_id).first():
        return jsonify({"message": "Application already exists"}), 409

    new_app = Application(student_id=user_id, drive_id=drive_id, status='Applied')
    db.session.add(new_app)
    db.session.commit()
    return jsonify({"message": "Applied successfully!"}), 201

@student_bp.route('/profile', methods=['GET', 'PUT'])
@jwt_required()
def manage_profile():
    user_id = get_jwt_identity()
    profile = StudentProfile.query.filter_by(user_id=user_id).first()
    
    if request.method == 'GET':
        return jsonify({
            "branch": profile.branch if profile else "",
            "cgpa": profile.cgpa if profile else 0.0,
            "resume_url": profile.resume_url if profile else None
        })
    
    data = request.get_json()
    if not profile:
        profile = StudentProfile(user_id=user_id)
        db.session.add(profile)
    
    profile.branch = data.get('branch')
    profile.cgpa = float(data.get('cgpa', 0.0))
    db.session.commit()
    return jsonify({"message": "Profile updated!"}), 200

@student_bp.route('/profile/resume', methods=['POST'])
@jwt_required()
def upload_resume():
    if 'resume' not in request.files:
        return jsonify({"message": "No file part"}), 400
    
    file = request.files['resume']
    if file and allowed_file(file.filename):
        user_id = get_jwt_identity()
        filename = secure_filename(f"resume_user_{user_id}.pdf")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        profile = StudentProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = StudentProfile(user_id=user_id)
            db.session.add(profile)
        
        profile.resume_url = filename
        db.session.commit()
        return jsonify({"message": "Resume uploaded successfully"}), 200
    
    return jsonify({"message": "Invalid file. Please upload a PDF."}), 400

@student_bp.route('/applications', methods=['GET'])
@jwt_required()
def get_my_applications():
    user_id = get_jwt_identity()
    my_apps = db.session.query(Application, PlacementDrive, CompanyProfile)\
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)\
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)\
        .filter(Application.student_id == user_id).all()
    
    return jsonify([{
        "id": app.id,
        "drive_id": drive.id,
        "company_name": company.company_name,
        "job_title": drive.job_title,
        "applied_on": app.application_date.strftime('%Y-%m-%d'),
        "status": app.status,
        "interview_date": app.interview_date 
    } for app, drive, company in my_apps]), 200

@student_bp.route('/export', methods=['POST'])
@jwt_required()
def trigger_export():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    export_student_applications_task.delay(user_id, user.email)
    return jsonify({"message": "Export started! Check MailHog shortly."}), 202
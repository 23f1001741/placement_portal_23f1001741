from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from models.models import db, User, CompanyProfile, StudentProfile

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()

    if user and check_password_hash(user.password, password):
        # Checking against 'active' column
        if not user.active:
            return jsonify({"message": "Account deactivated. Contact Admin."}), 403
            
        access_token = create_access_token(identity=str(user.id), additional_claims={'role': user.role})
        return jsonify(access_token=access_token, role=user.role), 200

    return jsonify({"message": "Invalid email or password"}), 401


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    username = data.get('username')

    if role == 'admin':
        return jsonify({"message": "Admin registration is not allowed."}), 403

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already registered"}), 409

    hashed_password = generate_password_hash(password)
    
    # active defaults to True in User model
    new_user = User(username=username, email=email, password=hashed_password, role=role)
    db.session.add(new_user)
    db.session.flush() 

    if role == 'company':
        new_company = CompanyProfile(
            user_id=new_user.id,
            company_name=data.get('company_name'),
            hr_contact=data.get('hr_contact'),
            website=data.get('website', '')
        )
        db.session.add(new_company)
    
    elif role == 'student':
        new_student = StudentProfile(
            user_id=new_user.id,
            branch=data.get('branch', ''),
            cgpa=float(data.get('cgpa', 0.0)),
            graduation_year=int(data.get('graduation_year', 2026))
        )
        db.session.add(new_student)

    db.session.commit()
    return jsonify({"message": f"{role.capitalize()} registered successfully. Please login."}), 201
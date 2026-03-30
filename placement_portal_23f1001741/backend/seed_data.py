import random
from datetime import datetime, timedelta
from app import app
from models.models import db, User, CompanyProfile, StudentProfile, PlacementDrive, Application
from werkzeug.security import generate_password_hash

def seed():
    with app.app_context():
        print("--> Clearing existing non-admin data...")
        # Order matters to avoid Foreign Key constraint errors
        Application.query.delete()
        PlacementDrive.query.delete()
        StudentProfile.query.delete()
        CompanyProfile.query.delete()
        User.query.filter(User.role != 'admin').delete()
        db.session.commit()

        # 1. Create 10 Companies
        print("--> Seeding 10 Companies (Auto-Approved)...")
        companies = []
        for i in range(1, 11):
            name = f"company{i}"
            email = f"hr@{name}.com"
            user = User(
                username=name, 
                email=email, 
                password=generate_password_hash(name), 
                role='company', 
                active=True
            )
            db.session.add(user)
            db.session.flush()
            
            profile = CompanyProfile(
                user_id=user.id, 
                company_name=f"{name.capitalize()} Corp", 
                hr_contact=f"HR_{name}", 
                website=f"https://{name}.com", 
                approval_status='Approved'
            )
            db.session.add(profile)
            companies.append(profile)

        # 2. Create 10 Students
        print("--> Seeding 10 Students with Random CGPAs...")
        branches = ["Computer Science", "Data Science", "Electronics", "Mechanical"]
        students = []
        for i in range(1, 11):
            name = f"student{i}"
            email = f"{name}@ppa.com"
            user = User(
                username=name, 
                email=email, 
                password=generate_password_hash(name), 
                role='student', 
                active=True
            )
            db.session.add(user)
            db.session.flush()
            
            test_cgpa = round(random.uniform(6.0, 9.8), 2)
            profile = StudentProfile(
                user_id=user.id, 
                branch=random.choice(branches), 
                cgpa=test_cgpa, 
                graduation_year=2026
            )
            db.session.add(profile)
            students.append(profile)

        db.session.commit()

        # 3. Create 10 Placement Drives
        print("--> Seeding 10 Placement Drives (Auto-Approved)...")
        roles = ["Software Engineer", "Full Stack Developer", "Data Scientist", "UI/UX Designer", "DevOps Engineer"]
        drives = []
        for i in range(1, 11):
            comp = random.choice(companies)
            req_cgpa = random.choice([6.0, 7.0, 8.0, 8.5])
            
            drive = PlacementDrive(
                company_id=comp.id,
                job_title=f"{random.choice(roles)}",
                job_description="Join our team to build next-generation scalable applications.",
                eligibility_criteria=f"Required Min CGPA: {req_cgpa}",
                minimum_cgpa=req_cgpa,
                application_deadline=datetime.now() + timedelta(days=random.randint(7, 30)),
                status='Approved'
            )
            db.session.add(drive)
            db.session.flush()
            drives.append(drive)

        db.session.commit()

        # 4. Create 20 Random Applications for Dashboard Charts
        print("--> Seeding 20 Applications (respecting CGPA eligibility)...")
        app_statuses = ['Applied', 'Shortlisted', 'Interview Scheduled', 'Selected', 'Rejected']
        count = 0
        while count < 20:
            student = random.choice(students)
            drive = random.choice(drives)
            
            # Check if already applied to this specific drive ID
            existing = Application.query.filter_by(student_id=student.user_id, drive_id=drive.id).first()
            
            # Check Eligibility
            if not existing and student.cgpa >= drive.minimum_cgpa:
                new_app = Application(
                    student_id=student.user_id,
                    drive_id=drive.id,
                    status=random.choice(app_statuses),
                    application_date=datetime.now() - timedelta(days=random.randint(1, 5))
                )
                # If Interview Scheduled, add a dummy date
                if new_app.status == 'Interview Scheduled':
                    new_app.interview_date = (datetime.now() + timedelta(days=random.randint(2, 10))).strftime('%Y-%m-%dT%H:%M')
                
                db.session.add(new_app)
                count += 1
        
        db.session.commit()

        print("\n" + "!"*40)
        print(" SEEDING COMPLETE ")
        print("!"*40)
        print(f"Entities: 10 Companies, 10 Students, 10 Drives, 20 Apps")
        print("Company Login: hr@company1.com  /  company1")
        print("Student Login: student1@ppa.com  /  student1")
        print("Admin Login:   admin@ppa.com     /  admin")
        print("!"*40)

if __name__ == "__main__":
    seed()
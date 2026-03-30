from celery import shared_task
from models.models import db, Application, User, StudentProfile, PlacementDrive, CompanyProfile
import csv
import os
import time
import smtplib
from email.message import EmailMessage
from jinja2 import Template

@shared_task(name="export_csv_task")
def export_csv_task(drive_id, company_email):
    print(f"--> [CELERY] Starting CSV export for drive {drive_id}...")
    
    time.sleep(5) 
    
    apps = Application.query.filter_by(drive_id=drive_id).all()
    
    os.makedirs('exports', exist_ok=True)
    filepath = f"exports/drive_{drive_id}_applications.csv"
    
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['App ID', 'Student Name', 'Email', 'Branch', 'CGPA', 'Status', 'Applied On'])
        
        for app in apps:
            user = User.query.get(app.student_id)
            profile = StudentProfile.query.filter_by(user_id=app.student_id).first()
            
            writer.writerow([
                app.id, 
                user.username if user else "N/A", 
                user.email if user else "N/A", 
                profile.branch if profile else "N/A", 
                profile.cgpa if profile else "N/A", 
                app.status, 
                app.application_date.strftime('%Y-%m-%d')
            ])
            
    # Send Email
    msg = EmailMessage()
    msg['Subject'] = f'Application Data Export - Drive {drive_id}'
    msg['From'] = 'noreply@ppa.com'
    msg['To'] = company_email
    msg.set_content("Your requested CSV export is attached.")

    with open(filepath, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='csv', filename=f'drive_{drive_id}.csv')

    try:
        with smtplib.SMTP('localhost', 1025) as server:
            server.send_message(msg)
    except Exception as e:
        print(f"Export Email Failed: {e}")
    
    return filepath

@shared_task(name="send_interview_notification")
def send_interview_notification(student_email, job_title, interview_date):
    print(f"--> [CELERY] Sending interview notification to {student_email}...")
    template_str = """
    <html>
        <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
            <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 8px;">
                <h2 style="color: #0d6efd;">Interview Invitation</h2>
                <p>Hello,</p>
                <p>An interview has been scheduled for your application:</p>
                <div style="background: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;">
                    <p style="margin: 0;"><strong>Position:</strong> {{ job_title }}</p>
                    <p style="margin: 0;"><strong>Date & Time:</strong> <span style="color: #0d6efd;">{{ date }}</span></p>
                </div>
                <p>Please log in to the Portal for details.</p>
            </div>
        </body>
    </html>
    """
    template = Template(template_str)
    html_content = template.render(job_title=job_title, date=interview_date)

    msg = EmailMessage()
    msg['Subject'] = f'Interview Scheduled: {job_title}'
    msg['From'] = 'noreply@ppa.com'
    msg['To'] = student_email
    msg.set_content(f"Interview for {job_title} on {interview_date}")
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP('localhost', 1025) as server:
            server.send_message(msg)
    except Exception as e:
        print(f"Notification Failed: {e}")
    return "Sent"

@shared_task(name="daily_student_reminder")
def daily_reminder_task():
    students = User.query.filter_by(role='student').all()
    for student in students:
        msg = EmailMessage()
        msg['Subject'] = 'Daily Placement Reminder'
        msg['From'] = 'admin@ppa.com'
        msg['To'] = student.email
        msg.set_content(f"Hello {student.username}, check the dashboard for new drives!")
        try:
            with smtplib.SMTP('localhost', 1025) as server:
                server.send_message(msg)
        except: pass
    return "Reminders sent"

@shared_task(name="monthly_admin_report")
def generate_monthly_report():
    stats = {
        "students": User.query.filter_by(role='student').count(),
        "drives": PlacementDrive.query.count(),
        "apps": Application.query.count()
    }
    template_str = "<html><body><h2>Monthly Report</h2><p>Students: {{ students }}</p></body></html>"
    html_content = Template(template_str).render(students=stats['students'])
    
    msg = EmailMessage()
    msg['Subject'] = 'Monthly Admin Report'
    msg['To'] = 'admin@ppa.com'
    msg['From'] = 'system@ppa.com'
    msg.add_alternative(html_content, subtype='html')
    
    try:
        with smtplib.SMTP('localhost', 1025) as server:
            server.send_message(msg)
    except: pass
    return "Report sent"

@shared_task(name="export_student_applications_task")
def export_student_applications_task(student_id, student_email):
    my_apps = db.session.query(Application, PlacementDrive, CompanyProfile)\
        .join(PlacementDrive, Application.drive_id == PlacementDrive.id)\
        .join(CompanyProfile, PlacementDrive.company_id == CompanyProfile.id)\
        .filter(Application.student_id == student_id).all()

    os.makedirs('exports', exist_ok=True)
    filepath = f"exports/student_{student_id}_history.csv"
    
    with open(filepath, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Student ID', 'Company Name', 'Drive Title', 'Status', 'Date'])
        for app, drive, company in my_apps:
            writer.writerow([student_id, company.company_name, drive.job_title, app.status, app.application_date.strftime('%Y-%m-%d')])

    msg = EmailMessage()
    msg['Subject'] = 'Your Application History'
    msg['From'] = 'noreply@ppa.com'
    msg['To'] = student_email
    msg.set_content("History attached.")
    with open(filepath, 'rb') as f:
        msg.add_attachment(f.read(), maintype='application', subtype='csv', filename='history.csv')

    try:
        with smtplib.SMTP('localhost', 1025) as server:
            server.send_message(msg)
    except: pass
    return filepath
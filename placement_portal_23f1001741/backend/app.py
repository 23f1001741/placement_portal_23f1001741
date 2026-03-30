import os
from flask import Flask, send_from_directory, jsonify
from models.models import db, User
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from werkzeug.security import generate_password_hash
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.company import company_bp
from routes.student import student_bp
from celery import Celery
from celery.schedules import crontab
from cache import cache

mail = Mail()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Database and Security
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ppa_database.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'super-secret-key-change-this-later' 

    # SMTP Configuration for MailHog
    app.config['MAIL_SERVER'] = 'localhost'
    app.config['MAIL_PORT'] = 1025
    app.config['MAIL_USE_TLS'] = False
    app.config['MAIL_USE_SSL'] = False

    # Celery Configuration
    app.config['broker_url'] = 'redis://localhost:6379/0'
    app.config['result_backend'] = 'redis://localhost:6379/0'

    # Flask-Caching Configurations (Redis)
    app.config['CACHE_TYPE'] = 'RedisCache'
    app.config['CACHE_REDIS_URL'] = 'redis://localhost:6379/0'
    app.config['CACHE_DEFAULT_TIMEOUT'] = 60 
    
    # Initialize Extensions
    db.init_app(app)
    jwt = JWTManager(app)
    cache.init_app(app)
    mail.init_app(app)

    # Register Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(company_bp, url_prefix='/api/company')
    app.register_blueprint(student_bp, url_prefix='/api/student')

    @app.route('/uploads/resumes/<filename>')
    def serve_resume(filename):
        upload_path = os.path.join(app.root_path, 'uploads', 'resumes')
        
        if not os.path.exists(os.path.join(upload_path, filename)):
            return jsonify({"message": "Resume file not found on server"}), 404
            
        return send_from_directory(upload_path, filename)

    return app

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['result_backend'],
        broker=app.config['broker_url']
    )
    
    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    celery.set_default()
    
    # Celery Beat Schedule
    celery.conf.beat_schedule = {
        'send-daily-reminders': {
            'task': 'daily_student_reminder',
            'schedule': crontab(hour=8, minute=0),
        },
        'send-monthly-report': {
            'task': 'monthly_admin_report',
            'schedule': crontab(day_of_month=1, hour=9, minute=0)
        }
    }
    
    return celery

app = create_app()
celery = make_celery(app)

# Programmatic DB Creation & Admin Setup
with app.app_context():
    db.create_all()
    if not User.query.filter_by(role='admin').first():
        admin = User(
            username='admin', 
            email='admin@ppa.com', 
            password=generate_password_hash('admin'), 
            role='admin',
            active=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created: admin@ppa.com")

if __name__ == '__main__':
    app.run(debug=True, port=5000)
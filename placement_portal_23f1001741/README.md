Professional Placement Portal (MAD2)
1. Project Overview
This application is a centralized platform for campus placements, featuring automated task scheduling, real-time statistics, and a decoupled architecture.

Core Components:

Frontend: Vue.js 3 (Vite) with Chart.js for data visualization.

Backend: Flask RESTful API with JWT authentication.

Database: SQLite with SQLAlchemy ORM.

Async Tasks: Celery with Redis as a message broker.

Scheduled Jobs: Celery Beat for daily reminders and monthly reports.

Caching: Flask-Caching (Redis) for optimized database queries.

2. Prerequisites
Ensure the following are installed and configured:

Python 3.12+

Node.js (LTS)

Redis Server: Running on localhost:6379.

MailHog: Download 'MailHog_windows_amd64.exe' from the official GitHub releases and place it in the root directory of this project.

3. Project Structure
placement_portal_23f1001741/
├── run.bat                # Master startup script
├── .gitignore             # Root ignore rules (Redis/Venv/SQLite)
├── MailHog.exe            # Downloaded email testing tool
├── backend/
│   ├── app.py             # Flask & Celery entry point
│   ├── tasks.py           # Background task definitions
│   └── requirements.txt   # Python dependencies
└── frontend/
    ├── src/               # Vue components and router
    └── package.json       # Node dependencies
    
4. Quick Start (Windows)
The project includes a master batch file to launch all services in separate windows for easier monitoring.

Start your Redis Server (via WSL or Windows service).

Ensure MailHog.exe is in the root folder.

Double-click run.bat.

This script will launch:

Redis (WSL)

MailHog UI

Flask Backend API (Port 5000)

Celery Worker (Solo pool)

Celery Beat Scheduler

Vue Frontend (Port 5173)

5. Manual Setup (Optional)
Backend:

Navigate to /backend.

Create virtual environment: python -m venv venv.

Activate: venv\Scripts\activate.

Install: pip install -r requirements.txt.

Run: python app.py.

Frontend:

Navigate to /frontend.

Install: npm install.

Run: npm run dev.

6. Access and Credentials
Portal UI: http://localhost:5173

MailHog (Emails): http://localhost:8025

Initial Admin Account:

Email: admin@ppa.com

Password: admin

7. Key Features
Admin Dashboard: Approve/Reject companies and placement drives. Master interview schedule tracking and student status search.

Company Dashboard: Create and manage drives, shortlist applicants, and export application data to CSV.

Student Dashboard: Profile management, real-time job application tracking, and automated email notifications for interviews.

Background Jobs: Automated daily email reminders for students and a monthly system-wide summary for admins.
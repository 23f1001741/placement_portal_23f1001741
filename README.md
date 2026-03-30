Professional Placement Portal (PPP) - MAD-2
Project Overview
This repository contains the full submission for the Modern Application Development II (MAD-2) course. The project is a multi-role placement management system built with a Flask REST API backend and a Vue.js 3 frontend. It features automated eligibility validation, real-time dashboards, and asynchronous background tasks using Celery and Redis.

Repository Structure
23f1001741_Project_Report_MAD_2.pdf: The comprehensive project report including the architecture description and AI usage declaration.

api.yaml: The exhaustive OpenAPI 3.0 specification for all system endpoints.

placement_portal_23f1001741/: The main source code directory containing both the backend and frontend services.

Quick Start Guide
1. Environment Setup
Navigate to the backend directory and install the required Python dependencies:
pip install -r requirements.txt

2. Database Initialization
Before running the application, populate the local SQLite database with sample data to enable all dashboard visualizations and testing workflows:
python seed_data.py

3. Running the Application
The project includes a run.bat file in the placement_portal_23f1001741 folder. Executing this file will attempt to start the following services simultaneously:

Flask Backend Server (Port 5000)

Vue.js Development Server (Port 5173)

Redis Server

Celery Worker and Celery Beat for background tasks

4. Testing Background Features
To verify automated email notifications and CSV exports, ensure MailHog is running. All system-generated emails can be viewed at http://localhost:8025.

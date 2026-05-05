TEAM TASK MANAGER
=================

A full-stack web application for managing teams, projects, and tasks with role-based access control.

LIVE URL
--------
https://web-production-6d615.up.railway.app

GITHUB REPOSITORY
-----------------
https://github.com/komalpoojari081-art/team-task-manager

TECH STACK
----------
- Backend: Python, Flask
- Database: SQLite with SQLAlchemy ORM
- Frontend: HTML, CSS
- Authentication: Flask-Login
- Deployment: Railway

FEATURES
--------
1. User Authentication (Signup/Login/Logout)
2. Role-Based Access Control (Admin/Member)
3. Admin Features:
   - Create and manage projects
   - Create tasks and assign to members
   - View all tasks and their status
   - See overdue tasks
   - View all team members
4. Member Features:
   - View assigned tasks
   - Update task status (Pending/In-Progress/Completed)
   - Personal dashboard with task stats

HOW TO RUN LOCALLY
------------------
1. Clone the repository
2. Create virtual environment: python -m venv venv
3. Activate: venv\Scripts\activate
4. Install packages: pip install -r requirements.txt
5. Run: python app.py
6. Open browser: http://127.0.0.1:5000

TEST CREDENTIALS
----------------
Admin:
  Email: admin@test.com
  Password: admin123

Member:
  Email: john@test.com
  Password: john123
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ---- MODELS ----
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False, default='member')

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    tasks = db.relationship('Task', backref='project', lazy=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')
    due_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('user.id'))
    assignee = db.relationship('User', backref='tasks')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            return redirect(url_for('member_dashboard'))
        return f(*args, **kwargs)
    return decorated

# ---- ROUTES ----
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('member_dashboard'))
        flash('Invalid email or password')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role', 'member')
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email already exists')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created! Please login.')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/admin/dashboard')
@login_required
@admin_required
def admin_dashboard():
    projects = Project.query.all()
    tasks = Task.query.all()
    members = User.query.filter_by(role='member').all()
    overdue = Task.query.filter(Task.due_date < datetime.utcnow(), Task.status != 'completed').all()
    return render_template('admin_dashboard.html', projects=projects, tasks=tasks, members=members, overdue=overdue)

@app.route('/admin/project/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        project = Project(name=name, description=description)
        db.session.add(project)
        db.session.commit()
        flash('Project created!')
        return redirect(url_for('admin_dashboard'))
    return render_template('create_project.html')

@app.route('/admin/task/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_task():
    projects = Project.query.all()
    members = User.query.filter_by(role='member').all()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        project_id = request.form.get('project_id')
        assigned_to = request.form.get('assigned_to')
        due_date = request.form.get('due_date')
        due_date = datetime.strptime(due_date, '%Y-%m-%d') if due_date else None
        task = Task(title=title, description=description, project_id=project_id, assigned_to=assigned_to, due_date=due_date)
        db.session.add(task)
        db.session.commit()
        flash('Task created!')
        return redirect(url_for('admin_dashboard'))
    return render_template('create_task.html', projects=projects, members=members)

@app.route('/member/dashboard')
@login_required
def member_dashboard():
    tasks = Task.query.filter_by(assigned_to=current_user.id).all()
    overdue = [t for t in tasks if t.due_date and t.due_date < datetime.utcnow() and t.status != 'completed']
    return render_template('member_dashboard.html', tasks=tasks, overdue=overdue)

@app.route('/member/task/<int:task_id>/update', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.assigned_to != current_user.id:
        flash('Not authorized')
        return redirect(url_for('member_dashboard'))
    task.status = request.form.get('status')
    db.session.commit()
    flash('Task updated!')
    return redirect(url_for('member_dashboard'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
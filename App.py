from flask import Flask, render_template, redirect, url_for, request

from flask_login import LoginManager, login_user, logout_user, current_user
from flask_security import Security, SQLAlchemySessionUserDatastore, roles_accepted
from db import db, User, Role

app = Flask(__name__)

# --- Configuration ---
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///g4g.sqlite3"  # Path to the SQLite database
app.config['SECRET_KEY'] = 'MY_SECRET'                            # Secret key for session management


db = SQLAlchemy(app)
with app.app_context():
    admin = Role(id=1, name='Admin')
    moderator = Role(id=2, name='Moderator')
    concorrents = Role(id=3, name='Contestants')

    db.session.add(admin)
    db.session.add(moderator)
    db.session.add(concorrents)

    db.session.commit()

    
# Flask-Security Setup 
user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
security = Security(app, user_datastore)

                    # Routes

# Home route renders index.html
@app.route('/')
def index():
    return render_template("index.html")

# Signup route for user registration
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    msg = ""
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            msg = "User already exists"
            return render_template("signup.html", msg=msg)
        user = User(email=request.form['email'], password=request.form['password'])
        role = Role.query.filter_by(id=int(request.form['options'])).first()
        if role:
            user.roles.append(role)
        else:
            msg = "Invalid role selection"
            return render_template("signup.html", msg=msg)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template("signup.html", msg=msg)

# Signin route for user login
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    msg = ""
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()
        if user:
            if user.password == request.form['password']:
                login_user(user)
                return redirect(url_for('index'))
            else:
                msg = "Wrong password"
        else:
            msg = "User doesn't exist"
        return render_template("signin.html", msg=msg)
    return render_template("signin.html", msg=msg)

# Logout route to end the session
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# Teachers route (Accessible to Admin only)
@app.route('/teachers')
@roles_accepted('Admin')
def teachers():
    teachers_list = []
    role_teachers = db.session.query(roles_users).filter_by(role_id=2).all()
    for teacher in role_teachers:
        user = User.query.filter_by(id=teacher.user_id).first()
        if user:
            teachers_list.append(user)
    return render_template("teachers.html", teachers=teachers_list)

# Staff route (Accessible to Admin and Teacher)
@app.route('/staff')
@roles_accepted('Admin', 'Teacher')
def staff():
    staff_list = []
    role_staff = db.session.query(roles_users).filter_by(role_id=3).all()
    for s in role_staff:
        user = User.query.filter_by(id=s.user_id).first()
        if user:
            staff_list.append(user)
    return render_template("staff.html", staff=staff_list)

# Students route (Accessible to Admin, Teacher, and Staff)
@app.route('/students')
@roles_accepted('Admin', 'Teacher', 'Staff')
def students():
    students_list = []
    role_students = db.session.query(roles_users).filter_by(role_id=4).all()
    for s in role_students:
        user = User.query.filter_by(id=s.user_id).first()
        if user:
            students_list.append(user)
    return render_template("students.html", students=students_list)

# My Details route (Accessible to all roles)
@app.route('/mydetails')
@roles_accepted('Admin', 'Teacher', 'Staff', 'Student')
def mydetails():
    return render_template("mydetails.html")
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from config import Config
from models import db, User, Student, Room, Payment, Notice

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not User.query.filter_by(email='admin@hostel.com').first():
        admin = User(name='System Admin', email='admin@hostel.com')
        admin.set_password('Admin@123')
        db.session.add(admin)
        db.session.commit()
        @app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # user already unnada check
        existing = User.query.filter_by(username=username).first()
        if existing:
            flash('Username already exists!')
            return redirect(url_for('signup'))
        
        new_user = User(username=username)
        new_user.set_password(password)  # password hash avuthundi
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created! Please login')
        return redirect(url_for('login'))
        
    return render_template('signup.html')

# --- AUTH ROUTES ---
@app.route('/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=True if request.form.get('remember') else False)
            return redirect(url_for('dashboard'))
        flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# --- MAIN ROUTES ---
@app.route('/dashboard')
@login_required
def dashboard():
    total_students = Student.query.count()
    total_rooms = Room.query.count()
    total_revenue = sum(p.amount for p in Payment.query.all())
    notices = Notice.query.order_by(Notice.date_posted.desc()).limit(5).all()
    return render_template('dashboard.html', 
                           total_students=total_students, 
                           total_rooms=total_rooms, 
                           total_revenue=total_revenue,
                           notices=notices)

# --- STUDENTS ---
@app.route('/students')
@login_required
def students():
    students_list = Student.query.all()
    return render_template('students.html', students=students_list)

@app.route('/student/add', methods=['GET', 'POST'])
@login_required
def student_add():
    if request.method == 'POST':
        try:
            new_student = Student(
                student_id=request.form['student_id'],
                full_name=request.form['full_name'],
                phone=request.form['phone'],
                email=request.form['email']
            )
            db.session.add(new_student)
            db.session.commit()
            flash('Student added successfully!', 'success')
            return redirect(url_for('students'))
        except Exception as e:
            db.session.rollback()
            flash('Error adding student. ID may already exist.', 'error')
    return render_template('student_form.html')

@app.route('/student/delete/<int:id>')
@login_required
def student_delete(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted.', 'success')
    return redirect(url_for('students'))

# --- ROOMS ---
@app.route('/rooms', methods=['GET', 'POST'])
@login_required
def rooms():
    rooms_list = Room.query.all()
    return render_template('rooms.html', rooms=rooms_list)

@app.route('/room/add', methods=['GET', 'POST'])
@login_required
def room_add():
    if request.method == 'POST':
        new_room = Room(
            room_number=request.form['room_number'],
            room_type=request.form['room_type'],
            capacity=request.form['capacity'],
            monthly_rent=request.form['monthly_rent']
        )
        db.session.add(new_room)
        db.session.commit()
        flash('Room added successfully!', 'success')
        return redirect(url_for('rooms'))
    return render_template('room_form.html')

# --- OTHER MODULES (Simplified Routing for Completeness) ---
@app.route('/admissions')
@login_required
def admissions(): return render_template('admissions.html')

@app.route('/payments')
@login_required
def payments(): return render_template('payments.html')

@app.route('/attendance')
@login_required
def attendance(): return render_template('attendance.html')

@app.route('/visitors')
@login_required
def visitors(): return render_template('visitors.html')

@app.route('/complaints')
@login_required
def complaints(): return render_template('complaints.html')

@app.route('/maintenance')
@login_required
def maintenance(): return render_template('maintenance.html')

@app.route('/mess')
@login_required
def mess(): return render_template('mess.html')

@app.route('/staff')
@login_required
def staff(): return render_template('staff.html')

@app.route('/notices')
@login_required
def notices(): return render_template('notices.html')

@app.route('/reports')
@login_required
def reports(): return render_template('reports.html')

@app.route('/settings')
@login_required
def settings(): return render_template('settings.html')

# --- ERROR HANDLERS ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(e):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
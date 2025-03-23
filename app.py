from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv

# โหลดโมเดลของฐานข้อมูล
from models import db, User, Village, Volunteer, TrainingType, Training, VolunteerTraining

# โหลดตัวแปรสภาพแวดล้อม
load_dotenv()

# สร้าง Flask app
app = Flask(__name__)

# การตั้งค่า Flask
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key_for_development')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'sqlite:///osm_database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# เชื่อมต่อฐานข้อมูล
db.init_app(app)

# ตั้งค่า Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'กรุณาเข้าสู่ระบบก่อนใช้งาน'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# สร้างฐานข้อมูลและผู้ใช้เริ่มต้น (admin)
# ใช้ with app.app_context() แทน before_first_request
with app.app_context():
    db.create_all()
    
    # ตรวจสอบว่ามีผู้ดูแลระบบหรือไม่
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        # ถ้ายังไม่มี ให้สร้างผู้ดูแลระบบ
        admin_password = os.getenv('ADMIN_PASSWORD', 'admin1234')
        hashed_password = generate_password_hash(admin_password)
        admin = User(
            username='admin',
            password=hashed_password,
            email='admin@example.com',
            first_name='ผู้ดูแล',
            last_name='ระบบ',
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()

# เพิ่มฟังก์ชัน now() สำหรับใช้ในเทมเพลต
@app.context_processor
def utility_processor():
    def now():
        return datetime.now()
    return dict(now=now)

# เส้นทาง (Routes)

# หน้าแรก
@app.route('/')
def index():
    if current_user.is_authenticated:
        # ข้อมูลสถิติสำหรับแสดงในหน้าแดชบอร์ด
        villages_count = Village.query.count()
        volunteers_count = Volunteer.query.count()
        trainings_count = Training.query.count()
        
        # ข้อมูล อสม. ตามหมู่บ้าน
        villages = Village.query.all()
        village_stats = []
        for village in villages:
            volunteers_in_village = Volunteer.query.filter_by(village_id=village.id).count()
            village_stats.append({
                'village': village,
                'count': volunteers_in_village
            })
            
        return render_template('dashboard.html', 
                               villages_count=villages_count,
                               volunteers_count=volunteers_count,
                               trainings_count=trainings_count,
                               village_stats=village_stats)
    else:
        return render_template('index.html')

# เข้าสู่ระบบ
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            flash('เข้าสู่ระบบสำเร็จ', 'success')
            return redirect(next_page or url_for('index'))
        else:
            flash('เข้าสู่ระบบไม่สำเร็จ โปรดตรวจสอบชื่อผู้ใช้และรหัสผ่าน', 'danger')
    
    return render_template('login.html')

# ออกจากระบบ
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ออกจากระบบสำเร็จ', 'success')
    return redirect(url_for('index'))

# รันแอปพลิเคชัน
if __name__ == '__main__':
    app.run(debug=True)
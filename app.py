from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
from dotenv import load_dotenv
from sqlalchemy import text

# โหลดโมเดลของฐานข้อมูล
from models import db, User, Village, Volunteer, Training, VolunteerTraining, ServiceUnit

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
            role='admin',
            service_unit_id=1  # Assign a default service unit ID for the admin
        )
        db.session.add(admin)
        db.session.commit()

    # Migration script to add training_type_id column if it doesn't exist
    with db.engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=off;"))
        result = conn.execute(text("PRAGMA table_info(training);"))
        columns = [row[1] for row in result]  # Access columns by index
        if 'training_type_id' not in columns:
            conn.execute(text("ALTER TABLE training ADD COLUMN training_type_id INTEGER;"))
        if 'service_unit_id' not in columns:
            conn.execute(text("ALTER TABLE training ADD COLUMN service_unit_id INTEGER NOT NULL DEFAULT 1;"))
        conn.execute(text("PRAGMA foreign_keys=on;"))

    # Migration script to add subdistrict column if it doesn't exist in volunteer table
    with db.engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=off;"))
        result = conn.execute(text("PRAGMA table_info(volunteer);"))
        columns = [row[1] for row in result]  # Access columns by index
        if 'subdistrict' not in columns:
            conn.execute(text("ALTER TABLE volunteer ADD COLUMN subdistrict VARCHAR(100) NOT NULL DEFAULT '';"))
        conn.execute(text("PRAGMA foreign_keys=on;"))

    # Migration script to add subdistrict and address columns if they don't exist in service_unit table
    with db.engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=off;"))
        result = conn.execute(text("PRAGMA table_info(service_unit);"))
        columns = [row[1] for row in result]  # Access columns by index
        if 'subdistrict' not in columns:
            conn.execute(text("ALTER TABLE service_unit ADD COLUMN subdistrict VARCHAR(100) NOT NULL DEFAULT '';"))
        if 'address' not in columns:
            conn.execute(text("ALTER TABLE service_unit ADD COLUMN address VARCHAR(255) NOT NULL DEFAULT '';"))
        conn.execute(text("PRAGMA foreign_keys=on;"))

    # Migration script to add subdistrict column if it doesn't exist in village table
    with db.engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=off;"))
        result = conn.execute(text("PRAGMA table_info(village);"))
        columns = [row[1] for row in result]  # Access columns by index
        if 'subdistrict' not in columns:
            conn.execute(text("ALTER TABLE village ADD COLUMN subdistrict VARCHAR(100) NOT NULL DEFAULT '';"))
        conn.execute(text("PRAGMA foreign_keys=on;"))

    # Migration script to add service_unit_id column if it doesn't exist in user table
    with db.engine.connect() as conn:
        conn.execute(text("PRAGMA foreign_keys=off;"))
        result = conn.execute(text("PRAGMA table_info(user);"))
        columns = [row[1] for row in result]  # Access columns by index
        if 'service_unit_id' not in columns:
            conn.execute(text("ALTER TABLE user ADD COLUMN service_unit_id INTEGER NOT NULL DEFAULT 1;"))
        conn.execute(text("PRAGMA foreign_keys=on;"))

    # Create service units if they don't exist
    service_units = [
        {'code': '10795', 'name': 'รพ.โคกเจริญ', 'subdistrict': 'ตำบลโคกเจริญ', 'address': 'ที่อยู่ 1'},
        {'code': '01542', 'name': 'รพ.สต.ยางราก', 'subdistrict': 'ตำบลยางราก', 'address': 'ที่อยู่ 2'},
        {'code': '01543', 'name': 'รพ.สต.ลำโป่งเพชร', 'subdistrict': 'ตำบลหนองมะค่า', 'address': 'ที่อยู่ 3'},
        {'code': '01544', 'name': 'รพ.สต.หนองมะค่า', 'subdistrict': 'ตำบลหนองมะค่า', 'address': 'ที่อยู่ 4'},
        {'code': '01545', 'name': 'รพ.สต.วังทอง', 'subdistrict': 'ตำบลวังทอง', 'address': 'ที่อยู่ 5'},
        {'code': '14270', 'name': 'รพ.สต.โคกแสมสาร', 'subdistrict': 'ตำบลโคกแสมสาร', 'address': 'ที่อยู่ 6'}
    ]
    for su in service_units:
        if not ServiceUnit.query.filter_by(code=su['code']).first():
            service_unit = ServiceUnit(code=su['code'], name=su['name'], subdistrict=su['subdistrict'], address=su['address'])
            db.session.add(service_unit)
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
        return redirect(url_for('dashboard'))
    else:
        return render_template('index.html')

# หน้าแดชบอร์ด
@app.route('/dashboard')
@login_required
def dashboard():
    if current_user.role == 'admin':
        # ข้อมูลสถิติสำหรับแสดงในหน้าแดชบอร์ด (admin เห็นข้อมูลทั้งหมด)
        villages_count = Village.query.count()
        volunteers_count = Volunteer.query.count()
        trainings_count = Training.query.count()
        
        # ข้อมูล อสม. ตามหมู่บ้าน
        villages = Village.query.all()
    else:
        # ข้อมูลสถิติสำหรับแสดงในหน้าแดชบอร์ด (user เห็นข้อมูลเฉพาะหน่วยบริการของตนเอง)
        villages_count = Village.query.filter_by(service_unit_id=current_user.service_unit_id).count()
        volunteers_count = Volunteer.query.filter_by(service_unit_id=current_user.service_unit_id).count()
        trainings_count = Training.query.filter_by(service_unit_id=current_user.service_unit_id).count()
        
        # ข้อมูล อสม. ตามหมู่บ้าน
        villages = Village.query.filter_by(service_unit_id=current_user.service_unit_id).all()
    
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
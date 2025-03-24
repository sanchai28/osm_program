# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin

db = SQLAlchemy()

# โมเดลสำหรับหน่วยบริการ
class ServiceUnit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    subdistrict = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)  # Add address field
    volunteers = db.relationship('Volunteer', backref='service_unit', lazy=True)
    villages = db.relationship('Village', backref='service_unit', lazy=True)
    trainings = db.relationship('Training', backref='service_unit', lazy=True)

    def __repr__(self):
        return f"{self.name} ({self.subdistrict})"

# โมเดลสำหรับทะเบียนหมู่บ้าน
class Village(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    village_number = db.Column(db.String(10), nullable=False)  # หมู่ที่
    village_name = db.Column(db.String(100), nullable=False)  # ชื่อหมู่บ้าน
    subdistrict = db.Column(db.String(100), nullable=False)  # Add subdistrict field
    volunteers = db.relationship('Volunteer', backref='village', lazy=True)  # ความสัมพันธ์กับ อสม.
    service_unit_id = db.Column(db.Integer, db.ForeignKey('service_unit.id'), nullable=False)
    
    def __repr__(self):
        return f"หมู่ {self.village_number} บ้าน{self.village_name}"

# โมเดลสำหรับทะเบียน อสม.
class Volunteer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.String(13), unique=True, nullable=False)  # เลขประจำตัว อสม. (same as id_card)
    id_card = db.Column(db.String(13), unique=True, nullable=False)  # เลขบัตรประชาชน
    title = db.Column(db.String(20), nullable=False)  # คำนำหน้า
    first_name = db.Column(db.String(100), nullable=False)  # ชื่อ
    last_name = db.Column(db.String(100), nullable=False)  # นามสกุล
    birth_date = db.Column(db.Date, nullable=False)  # วันเกิด
    address = db.Column(db.String(255), nullable=False)  # ที่อยู่
    phone = db.Column(db.String(10), nullable=False)  # เบอร์โทรศัพท์
    start_date = db.Column(db.Date, nullable=False)  # วันที่เริ่มเป็น อสม.
    status = db.Column(db.String(20), nullable=False, default='active')  # สถานะ (active/inactive)
    volunteer_type = db.Column(db.String(20), nullable=False)  # ประเภท อสม.
    subdistrict = db.Column(db.String(100), nullable=False)  # ตำบล
    
    # Foreign Key เชื่อมกับหมู่บ้าน
    village_id = db.Column(db.Integer, db.ForeignKey('village.id'), nullable=False)
    service_unit_id = db.Column(db.Integer, db.ForeignKey('service_unit.id'), nullable=False)
    
    # ความสัมพันธ์กับการอบรม
    trainings = db.relationship('VolunteerTraining', backref='volunteer', lazy=True)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.volunteer_id = self.id_card  # Set volunteer_id to id_card
    
    def __repr__(self):
        return f"{self.title}{self.first_name} {self.last_name}"

# โมเดลสำหรับประเภทการอบรม
class TrainingType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # ชื่อหลักสูตร
    description = db.Column(db.Text, nullable=True)  # รายละเอียด
    hours = db.Column(db.Integer, nullable=False)  # จำนวนชั่วโมง
    
    # ความสัมพันธ์กับการอบรม
    trainings = db.relationship('Training', backref='training_type', lazy=True)
    
    def __repr__(self):
        return f"{self.name} ({self.hours} ชั่วโมง)"

# โมเดลสำหรับการอบรม
class Training(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Ensure autoincrement is set
    title = db.Column(db.String(200), nullable=False)  # หัวข้อการอบรม
    description = db.Column(db.Text, nullable=True)  # รายละเอียด
    start_date = db.Column(db.Date, nullable=False)  # วันที่เริ่ม
    end_date = db.Column(db.Date, nullable=False)  # วันที่สิ้นสุด
    location = db.Column(db.String(255), nullable=False)  # สถานที่
    
    # Foreign Key เชื่อมกับประเภทการอบรม
    training_type_id = db.Column(db.Integer, db.ForeignKey('training_type.id'), nullable=False)
    service_unit_id = db.Column(db.Integer, db.ForeignKey('service_unit.id'), nullable=False)
        
    # ความสัมพันธ์กับ อสม. (Many-to-Many)
    attendees = db.relationship('VolunteerTraining', backref='training', lazy=True)
    
    def __repr__(self):
        return f"{self.title} ({self.start_date} ถึง {self.end_date})"

# โมเดลตารางเชื่อม อสม. กับการอบรม (ตาราง Many-to-Many)
class VolunteerTraining(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    volunteer_id = db.Column(db.Integer, db.ForeignKey('volunteer.id'), nullable=False)
    training_id = db.Column(db.Integer, db.ForeignKey('training.id'), nullable=False)
    status = db.Column(db.String(20), default='completed')  # สถานะการอบรม (completed/incomplete)
    score = db.Column(db.Float, nullable=True)  # คะแนน (ถ้ามี)
    certificate_number = db.Column(db.String(50), nullable=True)  # เลขที่วุฒิบัตร (ถ้ามี)
    
    def __repr__(self):
        return f"VolunteerTraining {self.id}"

# โมเดลสำหรับผู้ใช้งานระบบ
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # role: admin, user
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    service_unit_id = db.Column(db.Integer, db.ForeignKey('service_unit.id'), nullable=False)  # Add service_unit_id
    service_unit = db.relationship('ServiceUnit', backref='users')  # Add relationship to ServiceUnit

    def __repr__(self):
        return f"User: {self.username}"
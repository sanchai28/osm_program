# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, FloatField, DateField, PasswordField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, EqualTo, ValidationError
import re
from datetime import datetime

# ฟอร์มสำหรับการเข้าสู่ระบบ
class LoginForm(FlaskForm):
    username = StringField('ชื่อผู้ใช้', validators=[DataRequired()])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired()])
    remember = BooleanField('จดจำการเข้าสู่ระบบ')

# ฟอร์มสำหรับการลงทะเบียนผู้ใช้
class RegisterForm(FlaskForm):
    username = StringField('ชื่อผู้ใช้', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('รหัสผ่าน', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('ยืนยันรหัสผ่าน', validators=[DataRequired(), EqualTo('password')])
    email = StringField('อีเมล', validators=[DataRequired(), Email()])
    first_name = StringField('ชื่อ', validators=[DataRequired()])
    last_name = StringField('นามสกุล', validators=[DataRequired()])

# ฟอร์มสำหรับหมู่บ้าน
class VillageForm(FlaskForm):
    village_number = StringField('หมู่ที่', validators=[DataRequired()])
    village_name = StringField('ชื่อหมู่บ้าน', validators=[DataRequired()])
    
    def validate_village_number(self, field):
        # ตรวจสอบว่าหมู่ที่เป็นตัวเลขหรือไม่
        if not field.data.isdigit():
            raise ValidationError('หมู่ที่ต้องเป็นตัวเลขเท่านั้น')

# ฟอร์มสำหรับการค้นหาหมู่บ้าน
class VillageSearchForm(FlaskForm):
    search = StringField('ค้นหา')

# ฟอร์มสำหรับ อสม.
class VolunteerForm(FlaskForm):
    volunteer_id = StringField('เลขประจำตัว อสม.', validators=[DataRequired()])
    id_card = StringField('เลขบัตรประชาชน', validators=[DataRequired(), Length(min=13, max=13)])
    title_choices = [
        ('นาย', 'นาย'),
        ('นาง', 'นาง'),
        ('นางสาว', 'นางสาว')
    ]
    title = SelectField('คำนำหน้า', choices=title_choices, validators=[DataRequired()])
    first_name = StringField('ชื่อ', validators=[DataRequired()])
    last_name = StringField('นามสกุล', validators=[DataRequired()])
    birth_date = StringField('วันเกิด', validators=[DataRequired()])
    address = TextAreaField('ที่อยู่', validators=[DataRequired()])
    phone = StringField('เบอร์โทรศัพท์', validators=[DataRequired(), Length(min=10, max=10)])
    start_date = StringField('วันที่เริ่มเป็น อสม.', validators=[DataRequired()])
    status_choices = [
        ('active', 'ปฏิบัติงาน'),
        ('inactive', 'พักงาน')
    ]
    status = SelectField('สถานะ', choices=status_choices, validators=[DataRequired()])
    village_id = SelectField('หมู่บ้าน', coerce=int, validators=[DataRequired()])
    
    def validate_id_card(self, field):
        # ตรวจสอบว่าเลขบัตรประชาชนเป็นตัวเลข 13 หลัก
        if not field.data.isdigit() or len(field.data) != 13:
            raise ValidationError('เลขบัตรประชาชนต้องเป็นตัวเลข 13 หลัก')
    
    def validate_phone(self, field):
        # ตรวจสอบว่าเบอร์โทรศัพท์เป็นตัวเลข 10 หลัก
        if not field.data.isdigit() or len(field.data) != 10:
            raise ValidationError('เบอร์โทรศัพท์ต้องเป็นตัวเลข 10 หลัก')
    
    def validate_birth_date(self, field):
        try:
            datetime.strptime(field.data, '%Y-%m-%d')
        except ValueError:
            raise ValidationError('รูปแบบวันที่ไม่ถูกต้อง ต้องเป็น YYYY-MM-DD')
    
    def validate_start_date(self, field):
        try:
            datetime.strptime(field.data, '%Y-%m-%d')
        except ValueError:
            raise ValidationError('รูปแบบวันที่ไม่ถูกต้อง ต้องเป็น YYYY-MM-DD')

# ฟอร์มสำหรับการค้นหา อสม.
class VolunteerSearchForm(FlaskForm):
    name = StringField('ชื่อ-นามสกุล')
    village_id = SelectField('หมู่บ้าน', coerce=int, validators=[Optional()], choices=[('', 'ทั้งหมด')])
    status_choices = [
        ('', 'ทั้งหมด'),
        ('active', 'ปฏิบัติงาน'),
        ('inactive', 'พักงาน')
    ]
    status = SelectField('สถานะ', choices=status_choices, validators=[Optional()])

# ฟอร์มสำหรับประเภทการอบรม
class TrainingTypeForm(FlaskForm):
    name = StringField('ชื่อหลักสูตร', validators=[DataRequired()])
    description = TextAreaField('รายละเอียด', validators=[Optional()])
    hours = IntegerField('จำนวนชั่วโมง', validators=[DataRequired(), NumberRange(min=1)])

# ฟอร์มสำหรับการอบรม
class TrainingForm(FlaskForm):
    title = StringField('หัวข้อการอบรม', validators=[DataRequired()])
    description = TextAreaField('รายละเอียด', validators=[Optional()])
    start_date = StringField('วันที่เริ่ม', validators=[DataRequired()])
    end_date = StringField('วันที่สิ้นสุด', validators=[DataRequired()])
    location = StringField('สถานที่', validators=[DataRequired()])
    training_type_id = SelectField('ประเภทการอบรม', coerce=int, validators=[DataRequired()])
    
    def validate_start_date(self, field):
        try:
            datetime.strptime(field.data, '%Y-%m-%d')
        except ValueError:
            raise ValidationError('รูปแบบวันที่ไม่ถูกต้อง ต้องเป็น YYYY-MM-DD')

    def validate_end_date(self, field):
        try:
            end_date = datetime.strptime(field.data, '%Y-%m-%d')
            start_date = datetime.strptime(self.start_date.data, '%Y-%m-%d')
            if end_date < start_date:
                raise ValidationError('วันที่สิ้นสุดต้องมาหลังวันที่เริ่ม')
        except ValueError:
            raise ValidationError('รูปแบบวันที่ไม่ถูกต้อง ต้องเป็น YYYY-MM-DD')

# ฟอร์มสำหรับการค้นหาการอบรม
class TrainingSearchForm(FlaskForm):
    title = StringField('หัวข้อการอบรม')
    training_type_id = SelectField('ประเภทการอบรม', coerce=int, validators=[Optional()], choices=[('', 'ทั้งหมด')])
    start_date = StringField('วันที่เริ่ม', validators=[Optional()])
    end_date = StringField('วันที่สิ้นสุด', validators=[Optional()])

# ฟอร์มสำหรับการเพิ่ม อสม. เข้าร่วมการอบรม
class VolunteerTrainingForm(FlaskForm):
    volunteer_id = SelectField('อสม.', coerce=int, validators=[DataRequired()])
    status_choices = [
        ('completed', 'เสร็จสิ้น'),
        ('incomplete', 'ยังไม่เสร็จสิ้น')
    ]
    status = SelectField('สถานะการอบรม', choices=status_choices, validators=[DataRequired()])
    score = FloatField('คะแนน', validators=[Optional()])
    certificate_number = StringField('เลขที่วุฒิบัตร', validators=[Optional()])
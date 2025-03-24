# forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, FloatField, DateField, PasswordField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, EqualTo, ValidationError
from wtforms.widgets import ListWidget, CheckboxInput  # Add import for ListWidget and CheckboxInput
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
    service_unit_id = SelectField('หน่วยบริการ', coerce=int, validators=[DataRequired()])
    subdistrict = SelectField('ตำบล', choices=[
        ('ตำบลโคกเจริญ', 'ตำบลโคกเจริญ'),
        ('ตำบลยางราก', 'ตำบลยางราก'),
        ('ตำบลหนองมะค่า', 'ตำบลหนองมะค่า'),
        ('ตำบลวังทอง', 'ตำบลวังทอง'),
        ('ตำบลโคกแสมสาร', 'ตำบลโคกแสมสาร')
    ], validators=[DataRequired()])
    submit = SubmitField('บันทึก')
    
    def validate_village_number(self, field):
        # ตรวจสอบว่าหมู่ที่เป็นตัวเลขหรือไม่
        if not field.data.isdigit():
            raise ValidationError('หมู่ที่ต้องเป็นตัวเลขเท่านั้น')

# ฟอร์มสำหรับการค้นหาหมู่บ้าน
class VillageSearchForm(FlaskForm):
    search = StringField('ค้นหา')

# ฟอร์มสำหรับ อสม.
class VolunteerForm(FlaskForm):
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
        ('inactive', 'ลาออก')
    ]
    status = SelectField('สถานะ', choices=status_choices, validators=[DataRequired()])
    volunteer_type_choices = [
        ('บัญชี 1', 'บัญชี 1'),
        ('บัญชี 2', 'บัญชี 2')
    ]
    volunteer_type = SelectField('ประเภท อสม.', choices=volunteer_type_choices, validators=[DataRequired()])
    subdistrict = SelectField('ตำบล', choices=[
        ('ตำบลโคกเจริญ', 'ตำบลโคกเจริญ'),
        ('ตำบลยางราก', 'ตำบลยางราก'),
        ('ตำบลหนองมะค่า', 'ตำบลหนองมะค่า'),
        ('ตำบลวังทอง', 'ตำบลวังทอง'),
        ('ตำบลโคกแสมสาร', 'ตำบลโคกแสมสาร')
    ], validators=[DataRequired()])
    village_id = SelectField('หมู่บ้าน', coerce=int, validators=[DataRequired()])
    service_unit_id = SelectField('หน่วยบริการ', coerce=int, validators=[DataRequired()])
    submit = SubmitField('บันทึก')
    
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
    village_number = SelectField('หมู่ที่', coerce=lambda x: int(x) if x.isdigit() else None, validators=[Optional()])
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
    submit = SubmitField('บันทึก')

# ฟอร์มสำหรับการอบรม
class TrainingForm(FlaskForm):
    title = StringField('หัวข้อการอบรม', validators=[DataRequired()])
    description = TextAreaField('รายละเอียด', validators=[Optional()])
    start_date = StringField('วันที่เริ่ม', validators=[DataRequired()])
    end_date = StringField('วันที่สิ้นสุด', validators=[DataRequired()])
    location = StringField('สถานที่', validators=[DataRequired()])
    training_type_id = SelectField('ประเภทการอบรม', coerce=int, validators=[DataRequired()])  # Ensure this field is included
    subdistrict = SelectField('ตำบล', choices=[
        ('ตำบลโคกเจริญ', 'ตำบลโคกเจริญ'),
        ('ตำบลยางราก', 'ตำบลยางราก'),
        ('ตำบลหนองมะค่า', 'ตำบลหนองมะค่า'),
        ('ตำบลวังทอง', 'ตำบลวังทอง'),
        ('ตำบลโคกแสมสาร', 'ตำบลโคกแสมสาร')
    ], validators=[DataRequired()])
    service_unit_id = SelectField('หน่วยบริการ', coerce=int, validators=[DataRequired()])
    submit = SubmitField('บันทึก')
    
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
    search = StringField('ค้นหา อสม. โดยเลขบัตรประชาชนหรือชื่อ', validators=[Optional()])  # Add search field
    village_number = SelectField('กรองตามหมู่ที่', coerce=lambda x: int(x) if x.isdigit() else None, validators=[Optional()])  # Change to SelectField for village number
    volunteer_ids = SelectMultipleField('อสม.', coerce=int, option_widget=CheckboxInput(), widget=ListWidget(prefix_label=False), validators=[DataRequired()])  # Use SelectMultipleField with checkboxes
    volunteer_id = SelectField('อสม.', coerce=int, validators=[DataRequired()])  # Add volunteer_id field
    status = SelectField('สถานะการอบรม', choices=[('completed', 'สำเร็จ'), ('incomplete', 'ไม่สำเร็จ')], validators=[DataRequired()])  # Add status field
    score = FloatField('คะแนน', validators=[Optional()])  # Add score field
    certificate_number = StringField('เลขที่วุฒิบัตร', validators=[Optional()])  # Add certificate_number field
    submit = SubmitField('บันทึก')

    def validate_village_number(form, field):
        if field.data == '':
            field.data = None

# ฟอร์มสำหรับผู้ใช้
class UserForm(FlaskForm):
    username = StringField('ชื่อผู้ใช้', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('รหัสผ่าน', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('ยืนยันรหัสผ่าน', validators=[Optional(), EqualTo('password')])
    email = StringField('อีเมล', validators=[DataRequired(), Email()])
    first_name = StringField('ชื่อ', validators=[DataRequired()])
    last_name = StringField('นามสกุล', validators=[DataRequired()])
    role = SelectField('บทบาท', choices=[('admin', 'ผู้ดูแลระบบ'), ('user', 'ผู้ใช้ทั่วไป')], validators=[DataRequired()])
    service_unit_id = SelectField('หน่วยบริการ', coerce=int, validators=[DataRequired()])
    submit = SubmitField('บันทึก')
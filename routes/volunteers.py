# routes/volunteers.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from models import db, Volunteer, Village, Training, VolunteerTraining, ServiceUnit
from forms import VolunteerForm, VolunteerSearchForm
from datetime import datetime
import pandas as pd
import os

# สร้าง Blueprint สำหรับจัดการ อสม.
volunteers = Blueprint('volunteers', __name__, url_prefix='/volunteers')

# แสดงรายการ อสม. ทั้งหมด
@volunteers.route('/', methods=['GET', 'POST'])
@login_required
def list_volunteers():
    form = VolunteerSearchForm()
    
    # Set choices for village_number
    form.village_number.choices = [('', 'ทั้งหมด')] + [(v.village_number, f"หมู่ที่ {v.village_number}") for v in Village.query.distinct(Village.village_number).all()]
    
    # เริ่มต้นด้วยการค้นหาทั้งหมด
    if current_user.role == 'admin':
        query = Volunteer.query.join(Village)
    else:
        query = Volunteer.query.join(Village).filter(Volunteer.service_unit_id == current_user.service_unit_id)
    
    # ตรวจสอบการค้นหา
    if form.validate_on_submit():
        # ค้นหาตามหมู่บ้าน
        if form.village_number.data:
            query = query.filter(Village.village_number == form.village_number.data)
    
    # เรียงลำดับตามหมู่บ้านและชื่อ
    volunteers = query.order_by(Volunteer.village_id, Volunteer.first_name).all()
    
    # Group volunteers by village
    villages = {}
    for volunteer in volunteers:
        village = volunteer.village
        if village not in villages:
            villages[village] = []
        villages[village].append(volunteer)
    
    return render_template('volunteers/index.html', 
                          volunteers=volunteers, 
                          form=form, 
                          villages=villages)

# แสดงรายละเอียด อสม.
@volunteers.route('/<int:id>')
@login_required
def view_volunteer(id):
    volunteer = Volunteer.query.get_or_404(id)
    village = Village.query.get(volunteer.village_id)
    
    # ดึงประวัติการอบรม
    training_records = []
    volunteer_trainings = VolunteerTraining.query.filter_by(volunteer_id=id).all()
    
    for vt in volunteer_trainings:
        training = Training.query.get(vt.training_id)
        training_records.append({
            'volunteer_training': vt,
            'training': training
        })
    
    return render_template('volunteers/view.html', 
                          volunteer=volunteer,
                          village=village,
                          training_records=training_records)

# เพิ่ม อสม. ใหม่
@volunteers.route('/new', methods=['GET', 'POST'])
@login_required
def new_volunteer():
    form = VolunteerForm()
    form.service_unit_id.choices = [(su.id, su.name) for su in ServiceUnit.query.all()]
    
    # ดึงข้อมูลหมู่บ้านสำหรับ dropdown
    form.village_id.choices = [(v.id, f"หมู่ {v.village_number} บ้าน{v.village_name}") 
                              for v in Village.query.filter_by(subdistrict=form.subdistrict.data).all()]
    
    if form.validate_on_submit():
        # Check for duplicate id_card
        existing_by_idcard = Volunteer.query.filter_by(id_card=form.id_card.data).first()
        
        if existing_by_idcard:
            flash('เลขบัตรประชาชนนี้มีอยู่ในระบบแล้ว', 'danger')
            return render_template('volunteers/form.html', form=form, title='เพิ่ม อสม. ใหม่')
        
        # แปลงวันที่จากสตริงเป็น Date object
        birth_date = datetime.strptime(form.birth_date.data, '%Y-%m-%d').date()
        start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d').date()
        
        volunteer = Volunteer(
            id_card=form.id_card.data,
            volunteer_id=form.id_card.data,  # Set volunteer_id to id_card
            title=form.title.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            birth_date=birth_date,
            address=form.address.data,
            phone=form.phone.data,
            start_date=start_date,
            status=form.status.data,
            volunteer_type=form.volunteer_type.data,
            village_id=form.village_id.data,
            subdistrict=form.subdistrict.data,  # Add subdistrict field
            service_unit_id=form.service_unit_id.data
        )
        
        db.session.add(volunteer)
        db.session.commit()
        flash('เพิ่ม อสม. สำเร็จ', 'success')
        return redirect(url_for('volunteers.view_volunteer', id=volunteer.id))
        
    return render_template('volunteers/form.html', form=form, title='เพิ่ม อสม. ใหม่')

# แก้ไขข้อมูล อสม.
@volunteers.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_volunteer(id):
    volunteer = Volunteer.query.get_or_404(id)
    form = VolunteerForm(obj=volunteer)
    form.service_unit_id.choices = [(su.id, su.name) for su in ServiceUnit.query.all()]
    
    # ตั้งค่าตัวเลือกสำหรับหมู่บ้าน
    form.village_id.choices = [(v.id, f"หมู่ {v.village_number} บ้าน{v.village_name}") 
                              for v in Village.query.filter_by(subdistrict=form.subdistrict.data).all()]
    
    # ตั้งค่าค่าเริ่มต้นสำหรับวันที่
    if request.method == 'GET':
        form.birth_date.data = volunteer.birth_date.strftime('%Y-%m-%d')
        form.start_date.data = volunteer.start_date.strftime('%Y-%m-%d')
    
    if form.validate_on_submit():
        # ตรวจสอบว่าเลขบัตรประชาชนซ้ำหรือไม่ (ยกเว้นของ อสม. คนนี้)
        existing_by_idcard = Volunteer.query.filter(
            Volunteer.id_card == form.id_card.data,
            Volunteer.id != id
        ).first()
        
        if existing_by_idcard:
            flash('เลขบัตรประชาชนนี้มีอยู่ในระบบแล้ว', 'danger')
            return render_template('volunteers/form.html', form=form, title='แก้ไขข้อมูล อสม.', volunteer=volunteer)
        
        # แปลงวันที่จากสตริงเป็น Date object
        birth_date = datetime.strptime(form.birth_date.data, '%Y-%m-%d').date()
        start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d').date()
        
        # อัปเดตข้อมูล
        volunteer.id_card = form.id_card.data
        volunteer.volunteer_id = form.id_card.data  # Set volunteer_id to id_card
        volunteer.title = form.title.data
        volunteer.first_name = form.first_name.data
        volunteer.last_name = form.last_name.data
        volunteer.birth_date = birth_date
        volunteer.address = form.address.data
        volunteer.phone = form.phone.data
        volunteer.start_date = start_date
        volunteer.status = form.status.data
        volunteer.volunteer_type = form.volunteer_type.data
        volunteer.village_id = form.village_id.data
        volunteer.subdistrict = form.subdistrict.data  # Add subdistrict field
        volunteer.service_unit_id = form.service_unit_id.data
        
        db.session.commit()
        flash('แก้ไขข้อมูล อสม. สำเร็จ', 'success')
        return redirect(url_for('volunteers.view_volunteer', id=volunteer.id))
        
    return render_template('volunteers/form.html', form=form, title='แก้ไขข้อมูล อสม.', volunteer=volunteer)

# ลบข้อมูล อสม.
@volunteers.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_volunteer(id):
    volunteer = Volunteer.query.get_or_404(id)
    
    # ตรวจสอบว่ามีประวัติการอบรมหรือไม่
    trainings = VolunteerTraining.query.filter_by(volunteer_id=id).all()
    
    if trainings:
        # ลบประวัติการอบรมทั้งหมดก่อน
        for training in trainings:
            db.session.delete(training)
    
    db.session.delete(volunteer)
    db.session.commit()
    flash('ลบข้อมูล อสม. สำเร็จ', 'success')
    return redirect(url_for('volunteers.list_volunteers'))

# แสดงรายการ อสม. ตามหมู่บ้าน
@volunteers.route('/by-village/<int:village_id>')
@login_required
def volunteers_by_village(village_id):
    village = Village.query.get_or_404(village_id)
    volunteers = Volunteer.query.filter_by(village_id=village_id).order_by(Volunteer.first_name).all()
    return render_template('volunteers/by_village.html', 
                          village=village, 
                          volunteers=volunteers)

# หน้ารายงานสรุปข้อมูล อสม.
@volunteers.route('/report')
@login_required
def volunteer_report():
    # สรุปจำนวน อสม. ตามหมู่บ้าน
    villages = Village.query.all()
    village_stats = []
    for village in villages:
        active_count = Volunteer.query.filter_by(village_id=village.id, status='active').count()
        inactive_count = Volunteer.query.filter_by(village_id=village.id, status='inactive').count()
        total_count = active_count + inactive_count
        
        village_stats.append({
            'village': village,
            'active_count': active_count,
            'inactive_count': inactive_count,
            'total_count': total_count
        })
    
    # สรุปจำนวน อสม. แบ่งตามช่วงอายุ
    today = datetime.today().date()
    age_stats = {
        'less_than_30': 0,
        '30_to_40': 0,
        '40_to_50': 0,
        '50_to_60': 0,
        'more_than_60': 0
    }
    
    volunteers = Volunteer.query.all()
    for volunteer in volunteers:
        age = today.year - volunteer.birth_date.year - ((today.month, today.day) < (volunteer.birth_date.month, volunteer.birth_date.day))
        
        if age < 30:
            age_stats['less_than_30'] += 1
        elif 30 <= age < 40:
            age_stats['30_to_40'] += 1
        elif 40 <= age < 50:
            age_stats['40_to_50'] += 1
        elif 50 <= age < 60:
            age_stats['50_to_60'] += 1
        else:
            age_stats['more_than_60'] += 1
    
    # สรุปจำนวน อสม. ตามสถานะ
    status_stats = {
        'active': Volunteer.query.filter_by(status='active').count(),
        'inactive': Volunteer.query.filter_by(status='inactive').count()
    }
    
    return render_template('volunteers/report.html',
                          village_stats=village_stats,
                          age_stats=age_stats,
                          status_stats=status_stats,
                          total_volunteers=len(volunteers))

# ค้นหา อสม. ตามเลขประจำตัว
@volunteers.route('/search-by-id', methods=['GET', 'POST'])
@login_required
def search_by_volunteer_id():
    if request.method == 'POST':
        volunteer_id = request.form.get('volunteer_id')
        volunteer = Volunteer.query.filter_by(volunteer_id=volunteer_id).first()
        
        if volunteer:
            return redirect(url_for('volunteers.view_volunteer', id=volunteer.id))
        else:
            flash(f'ไม่พบ อสม. ที่มีเลขประจำตัว {volunteer_id}', 'warning')
    
    return render_template('volunteers/search_by_id.html')

# ค้นหา อสม. ตามเลขบัตรประชาชน
@volunteers.route('/search-by-idcard', methods=['GET', 'POST'])
@login_required
def search_by_idcard():
    if request.method == 'POST':
        id_card = request.form.get('id_card')
        volunteer = Volunteer.query.filter_by(id_card=id_card).first()
        
        if volunteer:
            return redirect(url_for('volunteers.view_volunteer', id=volunteer.id))
        else:
            flash(f'ไม่พบ อสม. ที่มีเลขบัตรประชาชน {id_card}', 'warning')
    
    return render_template('volunteers/search_by_idcard.html')

# หน้า index ของ อสม.
@volunteers.route('/index')
@login_required
def index():
    # ข้อมูลหมู่บ้านและ อสม. ในแต่ละหมู่บ้าน
    villages = Village.query.options(db.joinedload(Village.volunteers)).all()
    
    return render_template('volunteers/index.html', villages=villages)

@volunteers.route('/upload-excel', methods=['POST'])
@login_required
def upload_excel():
    if 'excel_file' not in request.files:
        flash('ไม่มีไฟล์ที่ถูกเลือก', 'danger')
        return redirect(url_for('volunteers.list_volunteers'))
    
    file = request.files['excel_file']
    if file.filename == '':
        flash('ไม่มีไฟล์ที่ถูกเลือก', 'danger')
        return redirect(url_for('volunteers.list_volunteers'))
    
    if file and file.filename.endswith('.xlsx'):
        try:
            df = pd.read_excel(file, dtype={'เบอร์โทรศัพท์': str})
            for index, row in df.iterrows():
                volunteer = Volunteer.query.filter_by(id_card=row['เลขบัตรประชาชน']).first()
                
                # Handle different date formats
                try:
                    birth_date = datetime.strptime(row['วันเกิด'], '%Y-%m-%d').date()
                except ValueError:
                    birth_date = datetime.strptime(row['วันเกิด'], '%d/%m/%Y').date()
                
                try:
                    start_date = datetime.strptime(row['วันที่เริ่มเป็น อสม.'], '%Y-%m-%d').date()
                except ValueError:
                    start_date = datetime.strptime(row['วันที่เริ่มเป็น อสม.'], '%d/%m/%Y').date()
                
                if volunteer:
                    # Update existing volunteer
                    volunteer.title = row['คำนำหน้า']
                    volunteer.first_name = row['ชื่อ']
                    volunteer.last_name = row['นามสกุล']
                    volunteer.birth_date = birth_date
                    volunteer.address = row['ที่อยู่']
                    volunteer.phone = row['เบอร์โทรศัพท์']
                    volunteer.start_date = start_date
                    volunteer.status = row['สถานะ']
                    volunteer.volunteer_type = row['ประเภท อสม.']
                    volunteer.village_id = Village.query.filter_by(village_number=row['หมู่ที่']).first().id
                else:
                    # Insert new volunteer
                    volunteer = Volunteer(
                        id_card=row['เลขบัตรประชาชน'],
                        title=row['คำนำหน้า'],
                        first_name=row['ชื่อ'],
                        last_name=row['นามสกุล'],
                        birth_date=birth_date,
                        address=row['ที่อยู่'],
                        phone=row['เบอร์โทรศัพท์'],
                        start_date=start_date,
                        status=row['สถานะ'],
                        volunteer_type=row['ประเภท อสม.'],
                        village_id=Village.query.filter_by(village_number=row['หมู่ที่']).first().id
                    )
                    db.session.add(volunteer)
            db.session.commit()
            flash('อัพโหลดข้อมูล อสม. สำเร็จ', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาดในการอัพโหลดข้อมูล: {str(e)}', 'danger')
    else:
        flash('ไฟล์ที่อัพโหลดต้องเป็นไฟล์ Excel (.xlsx)', 'danger')
    
    return redirect(url_for('volunteers.list_volunteers'))

@volunteers.route('/download-sample-excel')
@login_required
def download_sample_excel():
    sample_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'sample_volunteers.xlsx')
    return send_file(sample_file_path, as_attachment=True, download_name='sample_volunteers.xlsx')
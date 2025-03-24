# routes/trainings.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Training, Volunteer, VolunteerTraining, TrainingType, Village, ServiceUnit  # Add Village and ServiceUnit import
from forms import TrainingForm, TrainingSearchForm, VolunteerTrainingForm, TrainingTypeForm  # Add TrainingTypeForm import
from datetime import datetime

# สร้าง Blueprint สำหรับจัดการการอบรม
trainings = Blueprint('trainings', __name__, url_prefix='/trainings')


#################################
# การจัดการการอบรม
#################################

# แสดงรายการอบรมทั้งหมด
@trainings.route('/', methods=['GET', 'POST'])
@login_required
def list_trainings():
    form = TrainingSearchForm()
    
    # เริ่มต้นด้วยการค้นหาทั้งหมด
    if current_user.role == 'admin':
        query = Training.query
    else:
        query = Training.query.filter_by(service_unit_id=current_user.service_unit_id)
    
    # ตรวจสอบการค้นหา
    if form.validate_on_submit():
        # ค้นหาตามชื่อ
        if form.title.data:
            search_term = f"%{form.title.data}%"
            query = query.filter(Training.title.like(search_term))
        
        # ค้นหาตามช่วงวันที่
        if form.start_date.data and form.end_date.data:
            start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d').date()
            end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d').date()
            query = query.filter(Training.start_date >= start_date, Training.end_date <= end_date)
    
    trainings = query.order_by(Training.start_date.desc()).all()
    
    return render_template('trainings/index.html', 
                          trainings=trainings, 
                          form=form)

# แสดงรายละเอียดการอบรม
@trainings.route('/<int:id>')
@login_required
def view_training(id):
    training = Training.query.get_or_404(id)
    
    # ดึงข้อมูลผู้เข้าร่วมการอบรม
    attendees = VolunteerTraining.query.filter_by(training_id=id).all()
    
    return render_template('trainings/view.html', 
                          training=training, 
                          attendees=attendees)

# เพิ่มการอบรมใหม่
@trainings.route('/new', methods=['GET', 'POST'])
@login_required
def new_training():
    form = TrainingForm()
    
    # Set choices for training_type_id
    form.training_type_id.choices = [(tt.id, tt.name) for tt in TrainingType.query.all()]
    form.service_unit_id.choices = [(su.id, su.name) for su in ServiceUnit.query.all()]
    
    if form.validate_on_submit():
        try:
            # แปลงวันที่จากสตริงเป็น Date object
            start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d').date()
            end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d').date()
            
            training = Training(
                title=form.title.data,
                description=form.description.data,
                start_date=start_date,
                end_date=end_date,
                location=form.location.data,
                training_type_id=form.training_type_id.data,  # Set training_type_id
                subdistrict=form.subdistrict.data,  # Add subdistrict field
                service_unit_id=form.service_unit_id.data  # Set service_unit_id
            )
            
            db.session.add(training)
            db.session.commit()  # Ensure the instance is committed before redirecting
            flash('เพิ่มการอบรมสำเร็จ', 'success')
            return redirect(url_for('trainings.view_training', id=training.id))
        except Exception as e:
            db.session.rollback()
            flash(f'เกิดข้อผิดพลาดในการเพิ่มการอบรม: {str(e)}', 'danger')
    
    return render_template('trainings/form.html', form=form, title='เพิ่มการอบรมใหม่')

# แก้ไขข้อมูลการอบรม
@trainings.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_training(id):
    training = Training.query.get_or_404(id)
    form = TrainingForm(obj=training)
    
    # Set choices for training_type_id
    form.training_type_id.choices = [(tt.id, tt.name) for tt in TrainingType.query.all()]
    form.service_unit_id.choices = [(su.id, su.name) for su in ServiceUnit.query.all()]
    
    # ตั้งค่าค่าเริ่มต้นสำหรับวันที่
    if request.method == 'GET':
        form.start_date.data = training.start_date.strftime('%Y-%m-%d')
        form.end_date.data = training.end_date.strftime('%Y-%m-%d')
    
    if form.validate_on_submit():
        # แปลงวันที่จากสตริงเป็น Date object
        start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d').date()
        end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d').date()
        
        # อัปเดตข้อมูล
        training.title = form.title.data
        training.description = form.description.data
        training.start_date = start_date
        training.end_date = end_date
        training.location = form.location.data
        training.training_type_id = form.training_type_id.data  # Set training_type_id
        training.subdistrict = form.subdistrict.data  # Add subdistrict field
        training.service_unit_id = form.service_unit_id.data  # Set service_unit_id
        
        db.session.commit()
        flash('แก้ไขข้อมูลการอบรมสำเร็จ', 'success')
        return redirect(url_for('trainings.view_training', id=training.id))
    
    return render_template('trainings/form.html', form=form, title='แก้ไขข้อมูลการอบรม')

# ลบข้อมูลการอบรม
@trainings.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_training(id):
    training = Training.query.get_or_404(id)
    
    # ตรวจสอบว่ามีผู้เข้าร่วมการอบรมหรือไม่
    attendees = VolunteerTraining.query.filter_by(training_id=id).all()
    
    if attendees:
        # ลบข้อมูลผู้เข้าร่วมการอบรมทั้งหมดก่อน
        for attendee in attendees:
            db.session.delete(attendee)
    
    db.session.delete(training)
    db.session.commit()
    flash('ลบข้อมูลการอบรมสำเร็จ', 'success')
    return redirect(url_for('trainings.list_trainings'))

#################################
# การจัดการข้อมูลผู้เข้าร่วมการอบรม
#################################

# เพิ่มผู้เข้าร่วมการอบรม
@trainings.route('/<int:id>/add-volunteer', methods=['GET', 'POST'])
@login_required
def add_volunteer_to_training(id):
    training = Training.query.get_or_404(id)
    form = VolunteerTrainingForm()
    
    # Set choices for village_number
    form.village_number.choices = [('', 'ทั้งหมด')] + [(v.village_number, f"หมู่ที่ {v.village_number}") for v in Village.query.distinct(Village.village_number).all()]
    
    # ดึงรายการ อสม. ทั้งหมด
    query = Volunteer.query.join(Village)
    
    # ตรวจสอบการค้นหา
    if form.search.data:
        search_term = f"%{form.search.data}%"
        query = query.filter((Volunteer.id_card.like(search_term)) | (Volunteer.first_name.like(search_term)) | (Volunteer.last_name.like(search_term)))
    
    # ตรวจสอบการกรองตามหมู่ที่
    if form.village_number.data:
        query = query.filter(Village.village_number == form.village_number.data)
    
    available_volunteers = query.all()
    
    form.volunteer_ids.choices = [(v.id, f"{v.title}{v.first_name} {v.last_name} ({v.village.village_name})") for v in available_volunteers]
    
    if form.validate_on_submit():
        volunteer_ids = form.volunteer_ids.data
        for volunteer_id in volunteer_ids:
            attendee = VolunteerTraining(
                volunteer_id=volunteer_id,
                training_id=id,
                status=form.status.data,
                score=form.score.data,
                certificate_number=form.certificate_number.data
            )
            db.session.add(attendee)
        
        db.session.commit()
        flash('เพิ่มผู้เข้าร่วมการอบรมสำเร็จ', 'success')
        return redirect(url_for('trainings.view_training', id=id))
    
    return render_template('trainings/add_volunteer.html', 
                          form=form, 
                          training=training,
                          available_volunteers=available_volunteers)

# แก้ไขข้อมูลผู้เข้าร่วมการอบรม
@trainings.route('/volunteer-trainings/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_volunteer_training(id):
    attendee = VolunteerTraining.query.get_or_404(id)
    form = VolunteerTrainingForm(obj=attendee)
    
    # ตั้งค่า choices สำหรับ volunteer_id (แสดงเฉพาะ อสม. คนนี้)
    volunteer = Volunteer.query.get(attendee.volunteer_id)
    form.volunteer_id.choices = [(volunteer.id, f"{volunteer.title}{volunteer.first_name} {volunteer.last_name}")]
    
    if form.validate_on_submit():
        attendee.status = form.status.data
        attendee.score = form.score.data
        attendee.certificate_number = form.certificate_number.data
        
        db.session.commit()
        flash('แก้ไขข้อมูลผู้เข้าร่วมการอบรมสำเร็จ', 'success')
        return redirect(url_for('trainings.view_training', id=attendee.training_id))
    
    return render_template('trainings/edit_volunteer.html', 
                          form=form, 
                          attendee=attendee,
                          training=attendee.training)

# ลบข้อมูลผู้เข้าร่วมการอบรม
@trainings.route('/volunteer-trainings/<int:id>/delete', methods=['POST'])
@login_required
def delete_volunteer_training(id):
    attendee = VolunteerTraining.query.get_or_404(id)
    training_id = attendee.training_id
    
    db.session.delete(attendee)
    db.session.commit()
    flash('ลบข้อมูลผู้เข้าร่วมการอบรมสำเร็จ', 'success')
    return redirect(url_for('trainings.view_training', id=training_id))

# เพิ่มประเภทการอบรมใหม่
@trainings.route('/new-training-type', methods=['GET', 'POST'])
@login_required
def new_training_type():
    form = TrainingTypeForm()
    
    if form.validate_on_submit():
        training_type = TrainingType(
            name=form.name.data,
            description=form.description.data,
            hours=form.hours.data
        )
        
        db.session.add(training_type)
        db.session.commit()
        flash('เพิ่มประเภทการอบรมสำเร็จ', 'success')
        return redirect(url_for('trainings.list_trainings'))
    
    return render_template('trainings/add_training_type.html', form=form, title='เพิ่มประเภทการอบรม')
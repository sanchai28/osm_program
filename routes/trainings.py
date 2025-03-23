# routes/trainings.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Training, TrainingType, Volunteer, VolunteerTraining
from forms import TrainingForm, TrainingTypeForm, TrainingSearchForm, VolunteerTrainingForm
from datetime import datetime

# สร้าง Blueprint สำหรับจัดการการอบรม
trainings = Blueprint('trainings', __name__, url_prefix='/trainings')

#################################
# การจัดการประเภทการอบรม
#################################

# แสดงรายการประเภทการอบรมทั้งหมด
@trainings.route('/types')
@login_required
def list_training_types():
    training_types = TrainingType.query.all()
    return render_template('training_types/index.html', training_types=training_types)

# เพิ่มประเภทการอบรมใหม่
@trainings.route('/types/new', methods=['GET', 'POST'])
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
        return redirect(url_for('trainings.list_training_types'))
    
    return render_template('training_types/form.html', form=form, title='เพิ่มประเภทการอบรมใหม่')

# แก้ไขประเภทการอบรม
@trainings.route('/types/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_training_type(id):
    training_type = TrainingType.query.get_or_404(id)
    form = TrainingTypeForm(obj=training_type)
    
    if form.validate_on_submit():
        training_type.name = form.name.data
        training_type.description = form.description.data
        training_type.hours = form.hours.data
        db.session.commit()
        flash('แก้ไขประเภทการอบรมสำเร็จ', 'success')
        return redirect(url_for('trainings.list_training_types'))
    
    return render_template('training_types/form.html', form=form, title='แก้ไขประเภทการอบรม')

# ลบประเภทการอบรม
@trainings.route('/types/<int:id>/delete', methods=['POST'])
@login_required
def delete_training_type(id):
    training_type = TrainingType.query.get_or_404(id)
    
    # ตรวจสอบว่ามีการอบรมที่ใช้ประเภทนี้หรือไม่
    existing_trainings = Training.query.filter_by(training_type_id=id).first()
    if existing_trainings:
        flash('ไม่สามารถลบประเภทการอบรมได้ เนื่องจากมีการอบรมที่ใช้ประเภทนี้', 'danger')
        return redirect(url_for('trainings.list_training_types'))
    
    db.session.delete(training_type)
    db.session.commit()
    flash('ลบประเภทการอบรมสำเร็จ', 'success')
    return redirect(url_for('trainings.list_training_types'))

#################################
# การจัดการการอบรม
#################################

# แสดงรายการอบรมทั้งหมด
@trainings.route('/', methods=['GET', 'POST'])
@login_required
def list_trainings():
    form = TrainingSearchForm()
    
    # เริ่มต้นด้วยการค้นหาทั้งหมด
    query = Training.query
    
    # ตรวจสอบการค้นหา
    if form.validate_on_submit():
        # ค้นหาตามชื่อ
        if form.title.data:
            search_term = f"%{form.title.data}%"
            query = query.filter(Training.title.like(search_term))
        
        # ค้นหาตามประเภทการอบรม
        if form.training_type_id.data:
            query = query.filter(Training.training_type_id == form.training_type_id.data)
            
        # ค้นหาตามช่วงวันที่
        if form.start_date.data and form.end_date.data:
            start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d').date()
            end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d').date()
            query = query.filter(Training.start_date >= start_date, Training.end_date <= end_date)
    
    trainings = query.order_by(Training.start_date.desc()).all()
    
    # ดึงข้อมูลประเภทการอบรมสำหรับฟอร์มค้นหา
    training_types = TrainingType.query.all()
    
    return render_template('trainings/index.html', 
                          trainings=trainings, 
                          form=form, 
                          training_types=training_types)

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
    
    # ดึงข้อมูลประเภทการอบรมสำหรับ dropdown
    form.training_type_id.choices = [(t.id, t.name) for t in TrainingType.query.all()]
    
    if form.validate_on_submit():
        # แปลงวันที่จากสตริงเป็น Date object
        start_date = datetime.strptime(form.start_date.data, '%Y-%m-%d').date()
        end_date = datetime.strptime(form.end_date.data, '%Y-%m-%d').date()
        
        training = Training(
            title=form.title.data,
            description=form.description.data,
            start_date=start_date,
            end_date=end_date,
            location=form.location.data,
            training_type_id=form.training_type_id.data
        )
        
        db.session.add(training)
        db.session.commit()
        flash('เพิ่มการอบรมสำเร็จ', 'success')
        return redirect(url_for('trainings.view_training', id=training.id))
    
    return render_template('trainings/form.html', form=form, title='เพิ่มการอบรมใหม่')

# แก้ไขข้อมูลการอบรม
@trainings.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_training(id):
    training = Training.query.get_or_404(id)
    form = TrainingForm(obj=training)
    
    # ดึงข้อมูลประเภทการอบรมสำหรับ dropdown
    form.training_type_id.choices = [(t.id, t.name) for t in TrainingType.query.all()]
    
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
        training.training_type_id = form.training_type_id.data
        
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
    
    # ดึงรายการ อสม. ที่ยังไม่ได้เข้าร่วมการอบรมนี้
    existing_attendees = [a.volunteer_id for a in VolunteerTraining.query.filter_by(training_id=id).all()]
    available_volunteers = Volunteer.query.filter(Volunteer.id.notin_(existing_attendees)).all()
    
    form.volunteer_id.choices = [(v.id, f"{v.title}{v.first_name} {v.last_name}") 
                               for v in available_volunteers]
    
    if form.validate_on_submit():
        attendee = VolunteerTraining(
            volunteer_id=form.volunteer_id.data,
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
                          training=training)

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
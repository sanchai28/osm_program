# routes/villages.py
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Village, Volunteer
from forms import VillageForm

# สร้าง Blueprint สำหรับจัดการหมู่บ้าน
villages = Blueprint('villages', __name__, url_prefix='/villages')

# แสดงรายการหมู่บ้านทั้งหมด
@villages.route('/')
@login_required
def list_villages():
    villages = Village.query.all()
    return render_template('villages/index.html', villages=villages)

# แสดงรายละเอียดหมู่บ้าน
@villages.route('/<int:id>')
@login_required
def view_village(id):
    village = Village.query.get_or_404(id)
    volunteers = Volunteer.query.filter_by(village_id=id).all()
    return render_template('villages/view.html', village=village, volunteers=volunteers)

# เพิ่มหมู่บ้านใหม่
@villages.route('/new', methods=['GET', 'POST'])
@login_required
def new_village():
    form = VillageForm()
    
    if form.validate_on_submit():
        village = Village(
            village_number=form.village_number.data,
            village_name=form.village_name.data
        )
        db.session.add(village)
        db.session.commit()
        flash('เพิ่มหมู่บ้านสำเร็จ', 'success')
        return redirect(url_for('villages.list_villages'))
        
    return render_template('villages/form.html', form=form, title='เพิ่มหมู่บ้านใหม่')

# แก้ไขข้อมูลหมู่บ้าน
@villages.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_village(id):
    village = Village.query.get_or_404(id)
    form = VillageForm(obj=village)
    
    if form.validate_on_submit():
        village.village_number = form.village_number.data
        village.village_name = form.village_name.data
        db.session.commit()
        flash('แก้ไขข้อมูลหมู่บ้านสำเร็จ', 'success')
        return redirect(url_for('villages.view_village', id=village.id))
        
    return render_template('villages/form.html', form=form, title='แก้ไขข้อมูลหมู่บ้าน', village=village)

# ลบหมู่บ้าน
@villages.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_village(id):
    village = Village.query.get_or_404(id)
    
    # ตรวจสอบว่ามี อสม. อยู่ในหมู่บ้านหรือไม่
    volunteers = Volunteer.query.filter_by(village_id=id).first()
    if volunteers:
        flash('ไม่สามารถลบหมู่บ้านได้ เนื่องจากมี อสม. อยู่ในหมู่บ้านนี้', 'danger')
        return redirect(url_for('villages.view_village', id=village.id))
    
    db.session.delete(village)
    db.session.commit()
    flash('ลบหมู่บ้านสำเร็จ', 'success')
    return redirect(url_for('villages.list_villages'))
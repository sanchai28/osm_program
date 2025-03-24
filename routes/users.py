from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, ServiceUnit
from forms import UserForm
from werkzeug.security import generate_password_hash

# สร้าง Blueprint สำหรับจัดการผู้ใช้
users = Blueprint('users', __name__, url_prefix='/users')

# แสดงรายการผู้ใช้ทั้งหมด
@users.route('/')
@login_required
def list_users():
    if current_user.role != 'admin':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('index'))
    
    users = User.query.all()
    form = UserForm()  # Add this line to define the form variable
    return render_template('users/index.html', users=users, form=form)  # Pass the form variable to the template

# เพิ่มผู้ใช้ใหม่
@users.route('/new', methods=['GET', 'POST'])
@login_required
def new_user():
    if current_user.role != 'admin':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('index'))
    
    form = UserForm()
    form.service_unit_id.choices = [(su.id, su.name) for su in ServiceUnit.query.all()]
    
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            password=hashed_password,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            role=form.role.data,
            service_unit_id=form.service_unit_id.data
        )
        db.session.add(user)
        db.session.commit()
        flash('เพิ่มผู้ใช้สำเร็จ', 'success')
        return redirect(url_for('users.list_users'))
    
    return render_template('users/form.html', form=form, title='เพิ่มผู้ใช้ใหม่')

# แก้ไขข้อมูลผู้ใช้
@users.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(id):
    if current_user.role != 'admin':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    form.service_unit_id.choices = [(su.id, su.name) for su in ServiceUnit.query.all()]
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.role = form.role.data
        user.service_unit_id = form.service_unit_id.data
        
        if form.password.data:
            user.password = generate_password_hash(form.password.data)
        
        db.session.commit()
        flash('แก้ไขข้อมูลผู้ใช้สำเร็จ', 'success')
        return redirect(url_for('users.list_users'))
    
    return render_template('users/form.html', form=form, title='แก้ไขข้อมูลผู้ใช้')

# ลบผู้ใช้
@users.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete_user(id):
    if current_user.role != 'admin':
        flash('คุณไม่มีสิทธิ์เข้าถึงหน้านี้', 'danger')
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('ลบผู้ใช้สำเร็จ', 'success')
    return redirect(url_for('users.list_users'))

# routes/api.py
from flask import Blueprint, jsonify, request
from flask_login import login_required
from models import Village, Volunteer, Training, VolunteerTraining
from sqlalchemy.orm import joinedload
from datetime import datetime
from models import TrainingType



# สร้าง Blueprint สำหรับ API
api = Blueprint('api', __name__, url_prefix='/api')

##################################
# API สำหรับหมู่บ้าน
##################################

# ดึงข้อมูลหมู่บ้านทั้งหมด
@api.route('/villages', methods=['GET'])
@login_required
def get_villages():
    subdistrict = request.args.get('subdistrict')
    if subdistrict:
        villages = Village.query.filter_by(subdistrict=subdistrict).all()
        village_list = [{'id': v.id, 'village_number': v.village_number, 'village_name': v.village_name} for v in villages]
        return jsonify({'villages': village_list})
    villages = Village.query.all()
    result = []
    
    for village in villages:
        volunteers_count = Volunteer.query.filter_by(village_id=village.id).count()
        result.append({
            'id': village.id,
            'village_number': village.village_number,
            'village_name': village.village_name,
            'volunteers_count': volunteers_count
        })
    
    return jsonify(result)

# ดึงข้อมูลหมู่บ้านตาม ID
@api.route('/villages/<int:id>', methods=['GET'])
@login_required
def get_village(id):
    village = Village.query.get_or_404(id)
    volunteers = Volunteer.query.filter_by(village_id=id).all()
    
    volunteers_data = []
    for volunteer in volunteers:
        volunteers_data.append({
            'id': volunteer.id,
            'volunteer_id': volunteer.volunteer_id,
            'name': f"{volunteer.title}{volunteer.first_name} {volunteer.last_name}",
            'status': volunteer.status
        })
    
    result = {
        'id': village.id,
        'village_number': village.village_number,
        'village_name': village.village_name,
        'volunteers': volunteers_data,
        'volunteers_count': len(volunteers_data)
    }
    
    return jsonify(result)

##################################
# API สำหรับ อสม.
##################################

# ดึงข้อมูล อสม. ทั้งหมด
@api.route('/volunteers', methods=['GET'])
@login_required
def get_volunteers():
    # รับพารามิเตอร์การค้นหา
    village_id = request.args.get('village_id')
    status = request.args.get('status')
    
    # สร้างคิวรี่
    query = Volunteer.query
    
    # เพิ่มเงื่อนไขการค้นหา
    if village_id:
        query = query.filter_by(village_id=int(village_id))
    if status:
        query = query.filter_by(status=status)
    
    # ดึงข้อมูล
    volunteers = query.all()
    result = []
    
    for volunteer in volunteers:
        village = Village.query.get(volunteer.village_id)
        result.append({
            'id': volunteer.id,
            'volunteer_id': volunteer.volunteer_id,
            'id_card': volunteer.id_card,
            'name': f"{volunteer.title}{volunteer.first_name} {volunteer.last_name}",
            'birth_date': volunteer.birth_date.strftime('%Y-%m-%d'),
            'address': volunteer.address,
            'phone': volunteer.phone,
            'start_date': volunteer.start_date.strftime('%Y-%m-%d'),
            'status': volunteer.status,
            'village': {
                'id': village.id,
                'village_number': village.village_number,
                'village_name': village.village_name
            }
        })
    
    return jsonify(result)

# ดึงข้อมูล อสม. ตาม ID
@api.route('/volunteers/<int:id>', methods=['GET'])
@login_required
def get_volunteer(id):
    volunteer = Volunteer.query.get_or_404(id)
    village = Village.query.get(volunteer.village_id)
    
    # ดึงประวัติการอบรม
    trainings_data = []
    volunteer_trainings = VolunteerTraining.query.filter_by(volunteer_id=id).all()
    
    for vt in volunteer_trainings:
        training = Training.query.get(vt.training_id)
        training_type = TrainingType.query.get(training.training_type_id)
        
        trainings_data.append({
            'id': vt.id,
            'training': {
                'id': training.id,
                'title': training.title,
                'start_date': training.start_date.strftime('%Y-%m-%d'),
                'end_date': training.end_date.strftime('%Y-%m-%d'),
                'location': training.location,
                'training_type': {
                    'id': training_type.id,
                    'name': training_type.name,
                    'hours': training_type.hours
                }
            },
            'status': vt.status,
            'score': vt.score,
            'certificate_number': vt.certificate_number
        })
    
    result = {
        'id': volunteer.id,
        'volunteer_id': volunteer.volunteer_id,
        'id_card': volunteer.id_card,
        'title': volunteer.title,
        'first_name': volunteer.first_name,
        'last_name': volunteer.last_name,
        'full_name': f"{volunteer.title}{volunteer.first_name} {volunteer.last_name}",
        'birth_date': volunteer.birth_date.strftime('%Y-%m-%d'),
        'address': volunteer.address,
        'phone': volunteer.phone,
        'start_date': volunteer.start_date.strftime('%Y-%m-%d'),
        'status': volunteer.status,
        'village': {
            'id': village.id,
            'village_number': village.village_number,
            'village_name': village.village_name
        },
        'trainings': trainings_data,
        'trainings_count': len(trainings_data)
    }
    
    return jsonify(result)

##################################
# API สำหรับการอบรม
##################################

# ดึงข้อมูลการอบรมทั้งหมด
@api.route('/trainings', methods=['GET'])
@login_required
def get_trainings():
    # รับพารามิเตอร์การค้นหา
    training_type_id = request.args.get('training_type_id')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # สร้างคิวรี่
    query = Training.query
    
    # เพิ่มเงื่อนไขการค้นหา
    if training_type_id:
        query = query.filter_by(training_type_id=int(training_type_id))
    if start_date:
        query = query.filter(Training.start_date >= datetime.strptime(start_date, '%Y-%m-%d').date())
    if end_date:
        query = query.filter(Training.end_date <= datetime.strptime(end_date, '%Y-%m-%d').date())
    
    # ดึงข้อมูล
    trainings = query.all()
    result = []
    
    for training in trainings:
        training_type = TrainingType.query.get(training.training_type_id)
        attendees_count = VolunteerTraining.query.filter_by(training_id=training.id).count()
        
        result.append({
            'id': training.id,
            'title': training.title,
            'description': training.description,
            'start_date': training.start_date.strftime('%Y-%m-%d'),
            'end_date': training.end_date.strftime('%Y-%m-%d'),
            'location': training.location,
            'training_type': {
                'id': training_type.id,
                'name': training_type.name,
                'hours': training_type.hours
            },
            'attendees_count': attendees_count
        })
    
    return jsonify(result)

# ดึงข้อมูลการอบรมตาม ID
@api.route('/trainings/<int:id>', methods=['GET'])
@login_required
def get_training(id):
    training = Training.query.get_or_404(id)
    training_type = TrainingType.query.get(training.training_type_id)
    
    # ดึงข้อมูลผู้เข้าร่วมการอบรม
    attendees_data = []
    volunteer_trainings = VolunteerTraining.query.filter_by(training_id=id).all()
    
    for vt in volunteer_trainings:
        volunteer = Volunteer.query.get(vt.volunteer_id)
        village = Village.query.get(volunteer.village_id)
        
        attendees_data.append({
            'id': vt.id,
            'volunteer': {
                'id': volunteer.id,
                'volunteer_id': volunteer.volunteer_id,
                'name': f"{volunteer.title}{volunteer.first_name} {volunteer.last_name}",
                'village': {
                    'id': village.id,
                    'village_number': village.village_number,
                    'village_name': village.village_name
                }
            },
            'status': vt.status,
            'score': vt.score,
            'certificate_number': vt.certificate_number
        })
    
    result = {
        'id': training.id,
        'title': training.title,
        'description': training.description,
        'start_date': training.start_date.strftime('%Y-%m-%d'),
        'end_date': training.end_date.strftime('%Y-%m-%d'),
        'location': training.location,
        'training_type': {
            'id': training_type.id,
            'name': training_type.name,
            'hours': training_type.hours
        },
        'attendees': attendees_data,
        'attendees_count': len(attendees_data)
    }
    
    return jsonify(result)

##################################
# API สำหรับสถิติ
##################################

# ดึงข้อมูลสถิติภาพรวม
@api.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    villages_count = Village.query.count()
    volunteers_count = Volunteer.query.count()
    trainings_count = Training.query.count()
    
    # จำนวน อสม. ตามหมู่บ้าน
    villages = Village.query.all()
    villages_data = []
    
    for village in villages:
        volunteers_in_village = Volunteer.query.filter_by(village_id=village.id).count()
        villages_data.append({
            'id': village.id,
            'village_number': village.village_number,
            'village_name': village.village_name,
            'volunteers_count': volunteers_in_village
        })
    
    # จำนวนการอบรมตามประเภท
    training_types = TrainingType.query.all()
    training_types_data = []
    
    for tt in training_types:
        trainings_in_type = Training.query.filter_by(training_type_id=tt.id).count()
        training_types_data.append({
            'id': tt.id,
            'name': tt.name,
            'hours': tt.hours,
            'trainings_count': trainings_in_type
        })
    
    # สถานะ อสม.
    active_volunteers = Volunteer.query.filter_by(status='active').count()
    inactive_volunteers = Volunteer.query.filter_by(status='inactive').count()
    
    result = {
        'villages_count': villages_count,
        'volunteers_count': volunteers_count,
        'trainings_count': trainings_count,
        'villages': villages_data,
        'training_types': training_types_data,
        'volunteers_status': {
            'active': active_volunteers,
            'inactive': inactive_volunteers
        }
    }
    
    return jsonify(result)
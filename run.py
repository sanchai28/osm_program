# run.py
from app import app
from routes.villages import villages
from routes.volunteers import volunteers
from routes.trainings import trainings
from routes.api import api
from routes.users import users

# ลงทะเบียน Blueprints และกำหนด URL prefix เพื่อไม่ให้ซ้ำซ้อนกับเส้นทางหลัก
app.register_blueprint(villages)
app.register_blueprint(volunteers)
app.register_blueprint(trainings)
app.register_blueprint(api)
app.register_blueprint(users)

# เริ่มการทำงานของแอปพลิเคชัน
if __name__ == '__main__':
    app.run(debug=True)
from app.__init__ import create_app,db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # สร้างตารางในฐานข้อมูลถ้าหากยังไม่มี
    #app.run(debug=True)

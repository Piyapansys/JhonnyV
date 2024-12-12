# from flask import Flask
# from flask_restx import Api
# from flask_sqlalchemy import SQLAlchemy
# from app.routes import box_ns
# from app.config import Config

# # db = SQLAlchemy()  # ใช้ตัวเดียวกับใน models.py

# def create_app():
#     app = Flask(__name__)

#     # # ตั้งค่าการเชื่อมต่อกับฐานข้อมูล
#     # app.config.from_object(Config)  # โหลดการตั้งค่าจาก Config

#     # db.init_app(app)  # เชื่อมโยง db กับ app

#     api = Api(app, version='1.0', title='SYS DocFinder', description='API for Locate Document')

#     # Register blueprint for routes
#     api.add_namespace(box_ns)

#     return app

from flask import Flask
from flask_restx import Api
from flask_sqlalchemy import SQLAlchemy
from app.config import Config

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    
    api = Api(app, title='Document Box API', version='1.0', description='An API for managing document boxes')
    
    from app.routes import box_api,doc_api
    api.add_namespace(box_api)
    api.add_namespace(doc_api)

    return app

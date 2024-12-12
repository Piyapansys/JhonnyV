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

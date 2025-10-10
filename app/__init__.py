from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from app.routes.box import box_api
from app.routes.doc import doc_api
from app.routes.search import search_api
from app.routes.user import user_api
from app.routes.auth import auth_api

def create_app():
    app = Flask(__name__)
    
    # Configure CORS to allow requests from frontend
    CORS(app,
            origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://10.41.97.111:64401"],
            methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            allow_headers=["Content-Type", "Authorization", "X-Requested-With", "Accept", "Origin"],
            supports_credentials=True,
            expose_headers=["Content-Type", "Authorization"])

    
    api = Api(
        app,
        version='1.0',
        title='Johnny Voucher API',
        description='API for Johnny Voucher Application',
        doc='/api/docs'
    )
    
    # Register namespaces
    api.add_namespace(box_api)
    api.add_namespace(doc_api)
    api.add_namespace(search_api)
    api.add_namespace(user_api)
    api.add_namespace(auth_api)
    
    # Add root route
    @app.route('/')
    def index():
        return {
            "message": "Johnny Voucher API is running!",
            "version": "1.0",
            "docs": "/api/docs",
            "status": "active"
        }
    
    return app
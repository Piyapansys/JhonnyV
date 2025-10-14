from flask import Flask, send_from_directory
from flask_restx import Api
from flask_cors import CORS
import os
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
    
    # SPA fallback route - serve index.html for all non-API routes
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve_spa(path=''):
        # If the path starts with /api, let Flask handle it normally
        if path.startswith('api/'):
            return {"error": "API endpoint not found"}, 404
        
        # For root path, show API info
        if path == '':
            return {
                "message": "Johnny Voucher API is running!",
                "version": "1.0",
                "docs": "/api/docs",
                "status": "active"
            }
        
        # For all other paths, serve the frontend index.html
        frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'Johnny_Frontend', 'dist')
        
        # Check if the file exists in the dist folder
        if os.path.exists(frontend_path) and os.path.exists(os.path.join(frontend_path, 'index.html')):
            return send_from_directory(frontend_path, 'index.html')
        else:
            # Fallback if frontend is not built
            return {
                "message": "Frontend not built. Please run 'npm run build' in Johnny_Frontend directory",
                "api_docs": "/api/docs"
            }
    
    return app
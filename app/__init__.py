from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from app.config import Config
from app.db import get_db_connection
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
# Initialize the API object
api = Api(title="Johhny Voucher API", version="1.0", description="An API for managing document boxes")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize db with the Flask app
    db.init_app(app)

    # Initialize API with the Flask app
    api.init_app(app)

    # CORS(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    # Register namespaces
    from app.routes import box_api, doc_api, search_api
    api.add_namespace(box_api)
    api.add_namespace(doc_api)
    # api.add_namespace(upload_api)
    # api.add_namespace(trigger_api)
    api.add_namespace(search_api)
    # Test database connection (optional)
    try:
        conn = get_db_connection()  # Open the database connection
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # Simple query to verify the connection
        print("Database connection successful.")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database connection failed: {e}")
    
    return app

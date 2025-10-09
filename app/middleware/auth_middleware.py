from functools import wraps
from flask import request, jsonify
from app.models.auth import AuthModel

def token_required(f):
    """Decorator to check if a valid token is present in request"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return {"message": "Authorization header is missing or invalid"}, 401
        
        token = auth_header.split(' ')[1]
        
        # Validate token
        user_data = AuthModel.validate_token(token)
        if not user_data:
            return {"message": "Invalid or expired token"}, 401
        
        # Add user data to kwargs
        kwargs['user_data'] = user_data
        
        return f(*args, **kwargs)
    
    return decorated

def role_required(*required_permissions):
    """Decorator to check if user has required permissions"""
    def decorator(f):
        @wraps(f)
        @token_required
        def decorated_function(*args, **kwargs):
            user_data = kwargs.get('user_data')
            
            # Get user permissions
            permissions = AuthModel.get_user_permissions(user_data['role_id'])
            
            # Check if user has all required permissions
            for permission in required_permissions:
                if permission not in permissions or not permissions[permission]:
                    return {"message": f"Permission denied: {permission} is required"}, 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator

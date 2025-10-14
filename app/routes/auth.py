from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from app.models.auth import AuthModel
from app.db import get_db_connection

auth_api = Namespace('auth', description='Authentication operations')

login_model = auth_api.model('LoginModel', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

refresh_model = auth_api.model('RefreshModel', {
    'refresh_token': fields.String(required=True, description='Refresh token')
})

@auth_api.route('/login')
class LoginResource(Resource):
    @auth_api.expect(login_model)
    def post(self):
        """Authenticate user and return tokens"""
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')
            
            access_token, refresh_token = AuthModel.login(email, password)
            
            if not access_token or not refresh_token:
                return {"message": "Invalid credentials"}, 401
            
            return {
                "message": "Login successful",
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@auth_api.route('/refresh')
class RefreshResource(Resource):
    @auth_api.expect(refresh_model)
    def post(self):
        """Refresh access token"""
        try:
            data = request.json
            refresh_token = data.get('refresh_token')
            
            if not refresh_token:
                return {"message": "Refresh token is required"}, 400
            
            new_access_token = AuthModel.refresh_access_token(refresh_token)
            
            if not new_access_token:
                return {"message": "Invalid or expired refresh token"}, 401
            
            return {
                "message": "Token refreshed successfully",
                "access_token": new_access_token
            }, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@auth_api.route('/logout')
class LogoutResource(Resource):
    def post(self):
        """Logout user and invalidate tokens"""
        try:
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {"message": "Authorization header is missing or invalid"}, 401
            
            token = auth_header.split(' ')[1]
            
            # Validate token
            user_data = AuthModel.validate_token(token)
            if not user_data:
                return {"message": "Invalid or expired token"}, 401
            
            # Logout user
            success = AuthModel.logout(user_data['user_email'])
            
            if not success:
                return {"message": "Logout failed"}, 500
            
            return {"message": "Logout successful"}, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@auth_api.route('/validate')
class ValidateResource(Resource):
    def get(self):
        """Validate token and return user information"""
        try:
            # Get token from Authorization header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return {"message": "Authorization header is missing or invalid"}, 401
            
            token = auth_header.split(' ')[1]
            
            # Validate token
            user_data = AuthModel.validate_token(token)
            if not user_data:
                return {"message": "Invalid or expired token"}, 401
            
            # Get user permissions
            permissions = AuthModel.get_user_permissions(user_data['role_id'])
            
            # Get user info including is_approver
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT is_approver FROM Johnny_user WHERE user_email = ?", (user_data['user_email'],))
                user_info = cursor.fetchone()
                is_approver = user_info[0] if user_info else 0
            finally:
                cursor.close()
                conn.close()
            
            return {
                "message": "Token is valid",
                "user": user_data,
                "permissions": permissions,
                "is_approver": is_approver
            }, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@auth_api.route('/generate-token')
class GenerateTokenResource(Resource):
    def post(self):
        """Generate tokens for authenticated user (separate from johnny-login)"""
        try:
            data = request.json
            email = data.get('email')
            
            if not email:
                return {"message": "Email is required"}, 400
            
            # Generate tokens using our separate system
            access_token, refresh_token = AuthModel.generate_tokens(email)
            
            if not access_token or not refresh_token:
                return {"message": "Failed to generate tokens"}, 500
            
            return {
                "message": "Tokens generated successfully",
                "access_token": access_token,
                "refresh_token": refresh_token
            }, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
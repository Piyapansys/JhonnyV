from flask import request
from flask_restx import Namespace, Resource
from app.controllers import UserController
from app.middleware.auth_middleware import token_required, role_required

user_api = Namespace('api/user', description='User operations')

@user_api.route('/check-user')
class UserCheckResource(Resource):
    @user_api.doc(params={
        'user_email': 'user_email',
    })
    def get(self):
        """check if user exists by email (no token required)"""
        try:
            data = {
                    'user_email': request.args.get('user_email'),
                }
            result = UserController.get_user(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@user_api.route('/get-user')
class UserManageResource(Resource):
    @user_api.doc(params={
        'user_email': 'user_email',
    })
    @token_required
    def get(self, user_data=None):
        """get user by email (requires token)"""
        try:
            data = {
                    'user_email': request.args.get('user_email'),
                }
            result = UserController.get_user(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@user_api.route('/get-approver')
class ApproverResource(Resource):
    @token_required
    def get(self, user_data=None):
        """get approver"""
        try:
            result = UserController.get_approver()
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

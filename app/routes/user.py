from flask import request
from flask_restx import Namespace, Resource
from app.controllers import UserController
from app.middleware.auth_middleware import token_required, role_required

user_api = Namespace('user', description='User operations')

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

@user_api.route('/get-all-users')
class GetAllUsersResource(Resource):
    @token_required
    @role_required(['allow_user_manage'])
    def get(self, user_data=None):
        """get all users (requires allow_user_manage permission)"""
        try:
            result = UserController.get_all_users()
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@user_api.route('/create-user')
class CreateUserResource(Resource):
    @token_required
    @role_required(['allow_user_manage'])
    def post(self, user_data=None):
        """create new user (requires allow_user_manage permission)"""
        try:
            data = request.get_json()
            result = UserController.create_user(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@user_api.route('/update-user')
class UpdateUserResource(Resource):
    @token_required
    @role_required(['allow_user_manage'])
    def put(self, user_data=None):
        """update user (requires allow_user_manage permission)"""
        try:
            data = request.get_json()
            result = UserController.update_user(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@user_api.route('/delete-user')
class DeleteUserResource(Resource):
    @token_required
    @role_required(['allow_user_manage'])
    def delete(self, user_data=None):
        """delete user (requires allow_user_manage permission)"""
        try:
            user_email = request.args.get('user_email')
            if not user_email:
                return {"message": "user_email is required"}, 400
            result = UserController.delete_user({'user_email': user_email})
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@user_api.route('/get-all-roles')
class GetAllRolesResource(Resource):
    @token_required
    @role_required(['allow_user_manage'])
    def get(self, user_data=None):
        """get all roles (requires allow_user_manage permission)"""
        try:
            result = UserController.get_all_roles()
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@user_api.route('/create-role')
class CreateRoleResource(Resource):
    @token_required
    @role_required(['allow_user_manage'])
    def post(self, user_data=None):
        """create new role (requires allow_user_manage permission)"""
        try:
            data = request.get_json()
            result = UserController.create_role(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@user_api.route('/update-role')
class UpdateRoleResource(Resource):
    @token_required
    @role_required(['allow_user_manage'])
    def put(self, user_data=None):
        """update role (requires allow_user_manage permission)"""
        try:
            data = request.get_json()
            result = UserController.update_role(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@user_api.route('/delete-role')
class DeleteRoleResource(Resource):
    @token_required
    @role_required(['allow_user_manage'])
    def delete(self, user_data=None):
        """delete role (requires allow_user_manage permission)"""
        try:
            role_id = request.args.get('role_id')
            if not role_id:
                return {"message": "role_id is required"}, 400
            result = UserController.delete_role({'role_id': role_id})
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

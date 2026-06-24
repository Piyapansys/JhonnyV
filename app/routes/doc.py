from flask import request
from flask_restx import Namespace, Resource, fields
from app.controllers import DocController
from app.models.auth import AuthModel

doc_api = Namespace('api/docs', description='Document operations')

doc_model = doc_api.model('DocsModel', {
    'box_id': fields.String(required=True, description='Box ID'),
    'documents': fields.List(fields.String, required=True, description='List of document numbers'),
    'user_email': fields.String(required=True, description='User email')
})

approve_model = doc_api.model('ApprovePickupModel', {
    'approval_id': fields.String(required=True, description='approval_id'),
    'requester_email': fields.String(required=True, description='requester_email'),
    'approver_email': fields.String(required=True, description='approver_email'),
    'approval_detail': fields.String(required=True, description='approval_detail'),
})

update_status_model = doc_api.model('UpdateRequestStatusModel', {
    'approval_id': fields.String(required=True, description='approval_id'),
    'approval_status': fields.String(required=True, description='approval_status (approved or rejected)'),
    'approver_comment': fields.String(required=False, description='approver_comment'),
    'approval_response': fields.String(required=False, description='approval_response'),
})


def get_token_user():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None, ({"message": "Authorization header is missing or invalid"}, 401)
    token = auth_header.split(' ')[1]
    user_data = AuthModel.validate_token(token)
    if not user_data:
        return None, ({"message": "Invalid or expired token"}, 401)
    return user_data, None


def check_permission(user_data, permission):
    permissions = AuthModel.get_user_permissions(user_data['role_id'])
    if not permissions.get(permission):
        return ({"message": f"Permission denied: {permission} is required"}, 403)
    return None


@doc_api.route('/docInBox')
class DocMappingResource(Resource):
    @doc_api.expect(doc_model)
    def post(self):
        """Store documents into a box"""
        user_data, err = get_token_user()
        if err: return err
        perm_err = check_permission(user_data, 'allow_create')
        if perm_err: return perm_err
        try:
            result = DocController.store_doc(request.json)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500


@doc_api.route('/remove-docInBox')
class DocRemoveResource(Resource):
    @doc_api.expect(doc_model)
    def put(self):
        """Remove documents from a box"""
        user_data, err = get_token_user()
        if err: return err
        perm_err = check_permission(user_data, 'allow_pickup')
        if perm_err: return perm_err
        try:
            result = DocController.remove_docInBox(request.json)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500


@doc_api.route('/getDocDetail')
class DocGetResource(Resource):
    def get(self):
        """GET documents Detail"""
        user_data, err = get_token_user()
        if err: return err
        try:
            result = DocController.get_doc_detail()
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500


@doc_api.route('/getAllDocument')
class DocGetAllResource(Resource):
    def get(self):
        """GET All Documents Detail"""
        user_data, err = get_token_user()
        if err: return err
        try:
            result = DocController.get_all_document()
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500


@doc_api.route('/pickup-requests')
class PickupApproveResource(Resource):
    @doc_api.expect(approve_model)
    def post(self):
        """Approve Pickup Request"""
        user_data, err = get_token_user()
        if err: return err
        perm_err = check_permission(user_data, 'allow_pickup')
        if perm_err: return perm_err
        try:
            result = DocController.create_approve_pickup(request.json)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @doc_api.doc(params={
        'approval_id': 'approval_id',
        'requester_email': 'requester_email',
        'approver_email': 'approver_email',
        'status': 'status',
    })
    def get(self):
        """List of Pickup Request"""
        user_data, err = get_token_user()
        if err: return err
        try:
            data = {
                'approval_id': request.args.get('approval_id'),
                'requester_email': request.args.get('requester_email'),
                'approver_email': request.args.get('approver_email'),
                'status': request.args.get('status'),
            }
            result = DocController.get_pickup_request(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500


@doc_api.route('/update-request-status')
class UpdateRequestStatusResource(Resource):
    @doc_api.expect(update_status_model)
    def put(self):
        """Update approval request status"""
        user_data, err = get_token_user()
        if err: return err
        perm_err = check_permission(user_data, 'allow_pickup')
        if perm_err: return perm_err
        try:
            result = DocController.update_request_status(request.json)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500


@doc_api.route('/validate-pickup')
class ValidatePickupResource(Resource):
    @doc_api.expect(doc_model)
    def post(self):
        """Validate documents before creating pickup request"""
        user_data, err = get_token_user()
        if err: return err
        try:
            result = DocController.validate_pickup(request.json)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

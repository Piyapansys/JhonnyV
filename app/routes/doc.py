from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from app.controllers import DocController
from app.middleware.auth_middleware import token_required, role_required

doc_api = Namespace('api/docs', description='Document operations')

# Model for storing documents in a box
doc_model = doc_api.model('DocsModel', {
    'box_id': fields.String(required=True, description='Box ID'),
    'documents': fields.List(fields.String, required=True, description='List of document numbers'),
    'user_email': fields.String(required=True, description='User email')
})

@doc_api.route('/docInBox')
class DocMappingResource(Resource):
    @doc_api.expect(doc_model)
    @role_required('allow_create')
    def post(self, user_data=None):
        """Store documents into a box"""
        try:
            data = request.json
            result = DocController.store_doc(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500


@doc_api.route('/remove-docInBox')
class DocRemoveResource(Resource):
    @doc_api.expect(doc_model)
    @role_required('allow_pickup')
    def put(self, user_data=None):
        """Remove documents from a box"""
        try:
            data = request.json
            result = DocController.remove_docInBox(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
@doc_api.route('/getDocDetail')
class DocGetResource(Resource):
    @token_required
    def get(self, user_data=None):
        """GET documents Detail"""        
        try:
            result = DocController.get_doc_detail()
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
@doc_api.route('/getAllDocument')
class DocGetAllResource(Resource):
    @token_required
    def get(self, user_data=None):
        """GET All Documents Detail"""        
        try:
            result = DocController.get_all_document()
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
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
        
@doc_api.route('/pickup-requests')
class PickupApproveResource(Resource):
    @doc_api.expect(approve_model)
    @role_required('allow_pickup')
    def post(self, user_data=None):
        """Approve Pickup Request"""
        try:
            data = request.json
            result = DocController.create_approve_pickup(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500


    @doc_api.doc(params={
        'approval_id': 'approval_id',
        'requester_email': 'requester_email',
        'approver_email': 'approver_email',
        'status': 'status',
    })
    @token_required
    def get(self, user_data=None):
        """List of Pickup Request"""
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
    @role_required('allow_pickup')
    def put(self, user_data=None):
        """Update approval request status"""
        try:
            data = request.json
            result = DocController.update_request_status(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

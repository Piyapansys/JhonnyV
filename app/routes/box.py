from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from app.controllers import BoxController
from app.middleware.auth_middleware import token_required, role_required

box_api = Namespace('api/boxes', description='Box operations')

# Model for creating boxes
create_box_model = box_api.model('BoxCreateModel', {
    'box_type': fields.String(required=True, description='Type of box to create'),
    'box_year': fields.String(required=True, description='Year of the documents to store'),
    'create_amount': fields.Integer(required=True, default=1, description='Number of boxes to create'),
    'user_email': fields.String(required=True, description='User email'),
    'location' : fields.String(required=True, description='Box location')
})

# Model for updating box status
box_status_model = box_api.model('BoxStatusModel', {
    'box': fields.List(fields.String, required=True, description='List of boxes to update status'),
    'box_action': fields.String(required=True, description='Status to update'),
    'user_email': fields.String(required=True, description='User email'),
    'location': fields.Integer(required=True, description='Box Location'),
})

@box_api.route('/create_box')
class BoxCreateResource(Resource):
    @box_api.expect(create_box_model)
    @role_required('allow_create')
    def post(self, user_data=None):
        """Create a new box"""
        try:
            data = request.json
            result = BoxController.create_box(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@box_api.route('/update-status')
class BoxStatusResource(Resource):
    @box_api.expect(box_status_model)
    @role_required('allow_change')
    def put(self, user_data=None):
        """Update the status of one or more boxes"""
        try:
            data = request.json
            result = BoxController.update_box_status(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

boxtype_create_model = box_api.model('BoxTypeCreateModel', {
    'boxtype_id': fields.String(required=True, description='boxtype_id'),
    'boxtype_name': fields.String(required=True, description='boxtype_name'),
    'boxtype_shortname': fields.String(required=True, description='boxtype_shortname'),
})

boxtype_delete_model = box_api.model('BoxTypeDeleteModel', {
    'boxtype_id': fields.String(required=True, description='boxtype_id'),
})

@box_api.route('/box-types')
class BoxTypesResource(Resource):
    def options(self):
        """Handle preflight OPTIONS request"""
        return '', 200
    
    @token_required
    def get(self, user_data=None):
        """get all box types"""
        try:
            result = BoxController.get_box_types()
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
    
    @box_api.expect(boxtype_create_model)
    @role_required('allow_setting')
    def post(self, user_data=None):
        """Create a new box type"""
        try:
            data = request.json
            result = BoxController.create_box_doc_types(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
    @box_api.expect(boxtype_create_model)
    @role_required('allow_setting')
    def put(self, user_data=None):
        """Update box type"""
        try:
            data = request.json
            result = BoxController.update_box_doc_types(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @box_api.doc(params={
        'boxtype_id': 'boxtype_id',
    })  
    @role_required('allow_setting')
    def delete(self, user_data=None):
        """Delete a box type"""
        try:
            data = {
                    'boxtype_id': request.args.get('boxtype_id'),
                }
            result = BoxController.delete_box_doc_types(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

location_create_model = box_api.model('LocationCreateModel', {
    'location_name': fields.String(required=True, description='location_name'),
})

location_update_model = box_api.model('LocationUpdateModel', {
    'location_id': fields.Integer(required=True, description='location_id'),
    'location_name': fields.String(required=True, description='location_name'),
})

@box_api.route('/location')
class BoxLocationResource(Resource):
    def options(self):
        """Handle preflight OPTIONS request"""
        return '', 200
    
    @token_required
    def get(self, user_data=None):
        """Get all box locations"""
        try:
            result = BoxController.get_location()
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
    
    @box_api.expect(location_create_model)
    @role_required('allow_setting')
    def post(self, user_data=None):
        """Create a new box location"""
        try:
            data = request.json
            result = BoxController.create_location(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
    
    @box_api.expect(location_update_model)
    @role_required('allow_setting')
    def put(self, user_data=None):
        """Update box type"""
        try:
            data = request.json
            result = BoxController.update_location(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
    
    @box_api.doc(params={
        'location_id': 'location_id',
    })
    @role_required('allow_setting')
    def delete(self, user_data=None):
        """Delete a box location"""
        try:
            data = {
                    'location_id': request.args.get('location_id'),
                }
            result = BoxController.delete_location(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
@box_api.route('/destroy-box-by-year')
class DestroyBoxByYearResource(Resource):
    @box_api.doc(params={
        'box_year': {
            'description': 'Year of the documents to destroy (e.g., "2025")',
            'type': 'string',
            'required': True
        }
    })
    @role_required('allow_setting')
    def delete(self, user_data=None):
        """Destroy all boxes, documents, and related data for a specific year"""
        try:
            box_year = request.args.get('box_year')
            if not box_year:
                return {"message": "box_year parameter is required"}, 400
            
            data = {'box_year': box_year}
            result = BoxController.destroy_box_by_year(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

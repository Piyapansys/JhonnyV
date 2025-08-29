from http.client import HTTPException
from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from app.controllers import BoxController, DocController, SearchController
from app.config import Config
# --- Box Namespace ---
box_api = Namespace('api/boxes', description='Box operations')

config = Config()

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
    def post(self):
        """Create a new box"""
        try:
            data = request.json
            return BoxController.create_box(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@box_api.route('/update-status')
class BoxStatusResource(Resource):
    @box_api.expect(box_status_model)
    def put(self):
        """Update the status of one or more boxes"""
        try:
            data = request.json
            return BoxController.update_box_status(data)
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
    def get(self):
        """get all box types"""
        try:
            return BoxController.get_box_types()
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
    
    @box_api.expect(boxtype_create_model)
    def post(self):
        """Create a new box type"""
        try:
            data = request.json
            return BoxController.create_box_doc_types(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
    @box_api.expect(boxtype_create_model)
    def put(self):
        """Update box type"""
        try:
            data = request.json
            return BoxController.update_box_doc_types(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @box_api.doc(params={
        'boxtype_id': 'boxtype_id',
    })  
    def delete(self):
        """Delete a box type"""
        try:
            data = {
                    'boxtype_id': request.args.get('boxtype_id'),
                }
            return BoxController.delete_box_doc_types(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@box_api.route('/location')
class BoxLocationResource(Resource):
    def get(self):
        """Get all box locations"""
        try:
            return BoxController.get_box_locations()
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
    
    def post(self):
        """Create a new box location"""
        try:
            data = request.json
            return BoxController.create_box_location(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
    def put(self):
        """Update box location"""
        try:
            data = request.json
            return BoxController.update_box_location(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
    
    def delete(self):
        """Delete a box location"""
        try:
            data = request.json
            return BoxController.delete_box_location(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
destroy_box_model = box_api.model('DestroyBoxModel', {
    'box_year': fields.String(required=True, description='Year of the documents to destroy'),
})

@box_api.route('/destroy-box')
class DestroyBoxResource(Resource):
    @box_api.expect(destroy_box_model)
    def get(self):
        """Destroy THAT!! BOX Please"""
        try:
            return BoxController.get_box_types()
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

@box_api.errorhandler(HTTPException)
def handle_http_exception(error):
    """Handle HTTP exceptions with a structured response"""
    return jsonify({
        "message": error.description
    }), error.code


# --- Document Namespace ---
doc_api = Namespace('api/docs', description='Document operations')

# Model for storing documents in a box
doc_model = doc_api.model('DocsModel', {
    'box_id': fields.String(required=True, description='Box ID'),
    # 'document_year': fields.String(required=True, description='Year of the document'),
    #'Document_Type': fields.String(required=True, description='Type of the document'),
    'documents': fields.List(fields.String, required=True, description='List of document numbers'),
    'user_email': fields.String(required=True, description='User email')
})

@doc_api.route('/docInBox')
class DocMappingResource(Resource):
    @doc_api.expect(doc_model)
    def post(self):
        """Store documents into a box"""
        try:
            data = request.json
            return DocController.store_doc(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500


@doc_api.route('/remove-docInBox')
class DocRemoveResource(Resource):
    @doc_api.expect(doc_model)
    def put(self):
        """Remove documents from a box"""
        try:
            data = request.json
            return DocController.remove_docInBox(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
@doc_api.route('/getDocDetail')
class DocGetResource(Resource):
    def get(self):
        """GET documents Detail"""        
        try:
            documents = DocController.get_doc_detail()
            return documents  # Just return the data and status
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        
@doc_api.route('/getAllDocument')
class DocGetAllResource(Resource):
    def get(self):
        """GET All Documents Detail"""        
        try:
            documents = DocController.get_all_document()
            return documents  # Just return the data and status
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

search_api = Namespace('api/search', description='Search operations')

@search_api.route('')
# class DocSearchResource(Resource):
#     @search_api.doc(params={
#         'id': 'ID',
#         'year': 'Year of the document',
#         'type': 'Type of the document',
#         'location': 'Location of the document',
#         'category': 'Category of the document',
#     })
#     def get(self):
#         """Search documents using query parameters"""
#         try:
#             # ดึงค่าจาก query string
#             data = {
#                 'id': request.args.get('id'),
#                 'year': request.args.get('year'),
#                 'type': request.args.get('type'),
#                 'location': request.args.get('location'),
#                 'category': request.args.get('category')
#             }
#             return SearchController.search(data)
#         except Exception as e:
#             return {"message": f"An error occurred: {str(e)}"}, 500
class DocSearchResource(Resource):
    def get(self):
        """Search via query string (ใช้กับ performSearch)"""
        try:
            data = {
                'id': request.args.get('id'),
                'year': request.args.get('year'),
                'type': request.args.get('type'),
                'location': request.args.get('location'),
                'category': request.args.get('category')
            }
            return SearchController.search(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    def post(self):
        """Search via JSON payload (ใช้กับ Excel Upload)"""
        try:
            data = request.get_json()
            return SearchController.search(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

#asdasd
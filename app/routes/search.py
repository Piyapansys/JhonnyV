from flask import request
from flask_restx import Namespace, Resource
from app.controllers import SearchController
from app.middleware.auth_middleware import token_required

search_api = Namespace('search', description='Search operations')

@search_api.route('')
class DocSearchResource(Resource):
    @token_required
    def get(self, user_data=None):
        """Search via query string"""
        try:
            data = {
                'id': request.args.get('id'),
                'year': request.args.get('year'),
                'type': request.args.get('type'),
                'location': request.args.get('location'),
                'category': request.args.get('category')
            }
            result = SearchController.search(data)
            return result[0], result[1]
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    @token_required
    def post(self, user_data=None):
        """Search via JSON payload"""
        try:
            data = request.get_json()
            return SearchController.search(data)
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

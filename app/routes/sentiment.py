from flask import jsonify, request
from flask_restx import Namespace, Resource, fields
from app.models import SentimentNews

sentiment_api = Namespace('api/sentiment', description='Sentiment news operations')

@sentiment_api.route('')
class SentimentFeedbackResource(Resource):
    @sentiment_api.doc(params={
        'start_date': 'start_date',
        'end_date': 'end_date',
    })
    def get(self):
        """Get all sentiment feedback"""
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')

            result = SentimentNews.get_feedback(start_date=start_date, end_date=end_date)
            return result, 200
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
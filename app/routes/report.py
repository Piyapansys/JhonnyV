from flask import request
from flask_restx import Namespace, Resource

from app.controllers import ReportController
from app.middleware.auth_middleware import role_required

report_api = Namespace('api/report', description='Reporting operations')


@report_api.route('/dashboard')
class ReportDashboardResource(Resource):
    @role_required('allow_report')
    def get(self, user_data=None):
        limit = request.args.get('limit', default=10, type=int)
        months = request.args.get('months', default=6, type=int)

        if limit is None or limit <= 0:
            limit = 10
        if months is None or months <= 0:
            months = 6

        limit = min(limit, 50)
        months = min(months, 24)

        response, status_code = ReportController.get_dashboard_data(
            limit=limit,
            months=months,
        )
        return response, status_code


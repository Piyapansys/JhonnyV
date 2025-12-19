from flask import request
from flask_restx import Namespace, Resource

from app.controllers import ReportController
from app.middleware.auth_middleware import role_required

report_api = Namespace('api/report', description='Reporting operations')


@report_api.route('/dashboard')
class ReportDashboardResource(Resource):
    @role_required('allow_report')
    def get(self, user_data=None):
        limit = request.args.get('limit', default=None, type=int)
        months = request.args.get('months', default=6, type=int)
        days = request.args.get('days', default=7, type=int)

        if limit is not None and limit <= 0:
            limit = None
        if months is None or months <= 0:
            months = 6
        if days is None or days <= 0:
            days = 7

        # Allow returning more recent activities on the dashboard
        if limit is not None:
            limit = min(limit, 200)
        months = min(months, 24)
        days = min(days, 365)

        response, status_code = ReportController.get_dashboard_data(
            limit=limit,
            months=months,
            days=days,
        )
        return response, status_code


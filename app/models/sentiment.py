from datetime import datetime,timedelta, date
from decimal import Decimal
from uuid import uuid4
import pytz
from app.db import get_db_connection

class SentimentNews:
    @classmethod
    def get_feedback(cls, start_date: date = None, end_date: date = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            params = []
            query = """
                SELECT * FROM user_feedback
                WHERE user_email = 'jirawat.liwphrueksaphan@syssteel.com'
            """
            if start_date and end_date:
                query += " DATE(clicked_at) BETWEEN ? AND ?"
                params.append(approval_id)
                params.append(end_date)
            elif start_date:
                query += " DATE(clicked_at) >= ?"
                params.append(start_date)
            elif end_date:
                query += " DATE(clicked_at) <= ?"
                params.append(end_date)

            rows = cursor.execute(query, params)
            if not rows:
                return []
            return [map_row_to_dict(cursor, row) for row in rows]
        finally:
            cursor.close()
            conn.close()
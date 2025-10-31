from datetime import datetime,timedelta, date
from decimal import Decimal
from uuid import uuid4
import pytz
from collections import OrderedDict

from app.db import get_db_connection


class SentimentNews:
    @classmethod
    def get_feedback(cls, start_date: str = None, end_date: str = None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            params = []
            query = """
                SELECT * FROM user_feedback
                WHERE user_email = 'jirawat.liwphrueksaphan@syssteel.com'
            """

            if start_date and end_date:
                query += " AND clicked_at >= ? AND clicked_at <= ?"
                params.extend([start_date, end_date])
            elif start_date:
                query += " AND clicked_at >= ?"
                params.append(start_date)
            elif end_date:
                query += " AND clicked_at <= ?"
                params.append(end_date)

            cursor.execute(query, params)
            rows = cursor.fetchall()
            if not rows:
                return []

            return [map_row_to_dict(cursor, row) for row in rows]
        finally:
            cursor.close()
            conn.close()


def map_row_to_dict(cursor, row):
    """
    แปลงแถวข้อมูลจากฐานข้อมูลเป็น dictionary โดยอัตโนมัติ
    และทำความสะอาดข้อมูลประเภทข้อความ (string) ด้วยการลบช่องว่างข้างหน้าและข้างหลัง
    """
    columns = [column[0] for column in cursor.description]
    result = OrderedDict()

    for idx, column_name in enumerate(columns):
        value = row[idx]

        # ทำความสะอาดช่องว่างสำหรับข้อมูลข้อความ
        if isinstance(value, str):
            value = value.strip()

        # แปลง datetime เป็น string
        elif isinstance(value, datetime):
            value = value.strftime('%Y-%m-%d %H:%M:%S')

        # แปลง date เป็น string
        elif isinstance(value, date):
            value = value.strftime('%Y-%m-%d')

        # แปลง Decimal เป็น float
        elif isinstance(value, Decimal):
            value = float(value)

        result[column_name] = value

    return result
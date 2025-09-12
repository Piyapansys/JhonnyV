from datetime import datetime,timedelta, date
from decimal import Decimal
from uuid import uuid4
from app.db import get_db_connection
from collections import OrderedDict


class JohnnyBox:
    @classmethod
    def get_box_by_id(cls, box_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Johnny_box WHERE box_id = ?", (box_id,))
            row = cursor.fetchone()
            if row:
                return row  # Return the raw row or map to an object
            return None
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_all_box(cls):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT TOP (1000) [box_id]
                ,[box_year]
                ,[boxtype_id]
                ,[update_at]
                ,[update_by]
                ,[create_at]
                ,[create_by]    
                ,[location]
            FROM [dbo].[Johnny_box]
                """)
            row = cursor.fetchall()
            if row:
                return row  # Return the raw row or map to an object
            return None
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_box_types(cls):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT *
            FROM [dbo].[Johnny_boxType]
            """)
            rows = cursor.fetchall()
            if rows:
                return [map_row_to_dict(cursor, row) for row in rows]  # Return the raw row or map to an object
            return []
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def create_box_doc_type(cls,boxtype_id, boxtype_name, boxtype_shortname):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Johnny_boxType (boxtype_id, boxtype_name, boxtype_shortname, created_at)
                VALUES (?, ?, ?, ?)
            """, (boxtype_id, boxtype_name, boxtype_shortname, datetime.now()))
            cursor.execute("""
                INSERT INTO Johnny_docType (doctype_id, doctype_name, doctype_shortname, created_at)
                VALUES (?, ?, ?, ?)
            """, (boxtype_id, boxtype_name, boxtype_shortname, datetime.now()))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def update_box_doc_type(cls,boxtype_id, boxtype_name, boxtype_shortname):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Johnny_boxType 
                    SET boxtype_name = ?, boxtype_shortname = ?, created_at = ? 
                    WHERE boxtype_id = ?
            """, (boxtype_name, boxtype_shortname, datetime.now(), boxtype_id))
            cursor.execute("""
                UPDATE Johnny_docType 
                    SET doctype_name = ?, doctype_shortname = ?, created_at = ? 
                    WHERE doctype_id = ?
            """, (boxtype_name, boxtype_shortname, datetime.now(), boxtype_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def delete_box_doc_type(cls,boxtype_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM Johnny_boxType WHERE boxtype_id = ?
            """, (boxtype_id))
            cursor.execute("""
                DELETE FROM Johnny_docType WHERE doctype_id = ?
            """, (boxtype_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_location(cls):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT *
            FROM [dbo].[Johnny_location]
            """)
            rows = cursor.fetchall()
            if rows:
                return [map_row_to_dict(cursor, row) for row in rows]  # Return the raw row or map to an object
            return []
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def create_location(cls,location_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Johnny_location (location_name, created_at)
                VALUES ( ?, ?)
            """, ( location_name, datetime.now()))
            conn.commit()
        finally:
            cursor.close()
            conn.close()
        
    @classmethod
    def delete_location(cls,location_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                DELETE FROM Johnny_location WHERE location_id = ?
            """, (location_id))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_next_box_id(cls, box_year, box_type):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT TOP 1 box_number FROM Johnny_box 
                WHERE box_year = ? AND boxtype_id = ?
                ORDER BY box_number DESC
            """, (box_year, box_type))
            row = cursor.fetchone()
            next_box_number = 1 if row is None else row[0] + 1
            box_id = f"0490AC{box_year[2:]}J{box_type}{str(next_box_number).zfill(3)}"
            return box_id, next_box_number
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def create_box(cls, box_year, box_type, create_by, location):
        box_id, next_box_number = cls.get_next_box_id(box_year, box_type)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Johnny_box (box_id, boxtype_id, box_year, box_number, create_by, create_at, location_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (box_id, box_type, box_year, next_box_number, create_by, datetime.now(),location))
            conn.commit()
            return box_id
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def update_box_status(cls, box_action, user_email, box_number,location):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # ตรวจสอบว่า box_action เป็น OPEN หรือ CLOSE
            # if box_action in ["OPEN", "CLOSE"]:
            #     # สถานะเป็น 0 สำหรับ OPEN และ 1 สำหรับ CLOSE
            #     status = 0 if box_action == "OPEN" else 1

            #     cursor.execute("""
            #         UPDATE Johnny_box 
            #         SET box_close = ?, update_at = ?, update_by = ? 
            #         WHERE box_id = ?
            #     """, (status, datetime.now() + timedelta(hours=7), user_email, box_number))
            #     conn.commit()

            # ตรวจสอบว่า box_action เป็น RELOCATE
            if box_action == "RELOCATE":
                # การอัพเดตเมื่อ box_action เป็น RELOCATE
                cursor.execute("""
                    UPDATE Johnny_box 
                    SET location_id = ?, update_at = ?, update_by = ? 
                    WHERE box_id = ?
                """, (location, datetime.now() + timedelta(hours=7), user_email, box_number))
                conn.commit()
        finally:
            cursor.close()
            conn.close()


class JohnnyDoc:

    @classmethod
    def create_doc(cls, doc_year, doctype_id, doc_number, store_by):
        doc_id = f"{doc_year}{doc_number}"
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Johnny_doc WHERE doc_id = ?", (doc_id,))
            row = cursor.fetchone()

            if row:
                cursor.execute("""
                    UPDATE Johnny_doc 
                    SET store_at = ?, store_by = ? 
                    WHERE doc_id = ?
                """, (datetime.now()+ timedelta(hours=7), store_by, doc_id))
            else:
                cursor.execute("""
                    INSERT INTO Johnny_doc (doc_id, doctype_id, doc_year, doc_number, store_by, store_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (doc_id, doctype_id, doc_year, doc_number, store_by, datetime.now()))
            conn.commit()
            return doc_id
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_document_detail(cls):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT doc.doc_id
                ,doc.doc_year
                ,doc.doctype_id
                ,doc.doc_number
                ,doc.remove_at
                ,doc.remove_by
                ,doc.store_at
                ,doc.store_by
                ,docinbox.box_id
                ,box.box_year
                ,box.boxtype_id
                ,box.location
            FROM [dbo].[Johnny_doc] doc
            LEFT JOIN [dbo].[Johnny_docInBox] docinbox ON doc.doc_id = docinbox.doc_id
            LEFT JOIN [dbo].[Johnny_box] box ON docinbox.box_id = box.box_id
            WHERE 
                (DATEDIFF(DAY, doc.store_at, GETDATE()) <= 1 OR
                DATEDIFF(DAY, doc.remove_at, GETDATE()) <= 1 OR
                DATEDIFF(DAY, box.update_at, GETDATE()) <= 1 OR
                DATEDIFF(DAY, box.create_at, GETDATE()) <= 1)
            """)
            rows = cursor.fetchall()  # ใช้ fetchall เพื่อดึงข้อมูลทั้งหมด
            if not rows:
                return []  # หากไม่มีข้อมูล ให้คืนค่าเป็น list ว่างๆ

            columns = [column[0] for column in cursor.description]


            def convert_datetime(value):
                if isinstance(value, datetime):
                    return value.isoformat()  # หรือใช้ str(value) ก็ได้
                return value
            
            # แปลงแต่ละแถวให้เป็น dictionary และแปลง datetime ให้เป็น string
            result = [dict(zip(columns, [convert_datetime(value) for value in row])) for row in rows]
            return result
        except Exception as e:
            print(f"Database error: {str(e)}")  # Add logging
            raise  # Re-raise the exception to be caught by the controller
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_all_document(cls):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
            SELECT doc.doc_id
                ,doc.doc_year
                ,doc.doctype_id
                ,doc.doc_number
                ,doc.remove_at
                ,doc.remove_by
                ,doc.store_at
                ,doc.store_by
                ,docinbox.box_id
                ,box.box_year
                ,box.boxtype_id
                ,box.location
            FROM [dbo].[Johnny_doc] doc
            LEFT JOIN [dbo].[Johnny_docInBox] docinbox ON doc.doc_id = docinbox.doc_id
            LEFT JOIN [dbo].[Johnny_box] box ON docinbox.box_id = box.box_id
            """)
            rows = cursor.fetchall()  # ใช้ fetchall เพื่อดึงข้อมูลทั้งหมด
            if not rows:
                return []  # หากไม่มีข้อมูล ให้คืนค่าเป็น list ว่างๆ

            columns = [column[0] for column in cursor.description]


            def convert_datetime(value):
                if isinstance(value, datetime):
                    return value.isoformat()  # หรือใช้ str(value) ก็ได้
                return value
            
            # แปลงแต่ละแถวให้เป็น dictionary และแปลง datetime ให้เป็น string
            result = [dict(zip(columns, [convert_datetime(value) for value in row])) for row in rows]
            return result
        except Exception as e:
            print(f"Database error: {str(e)}")  # Add logging
            raise  # Re-raise the exception to be caught by the controller
        finally:
            cursor.close()
            conn.close()


class DocInBox:
    
    @classmethod
    def create_docInBox(cls, id, doc_id, box_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Johnny_docInBox WHERE doc_id = ?", (doc_id,))
            row = cursor.fetchone()
            if row:
                row_dict = dict(zip([column[0] for column in cursor.description], row))
                # แถวที่ select มาแล้ว ตรวจสอบค่า box_id
                if row_dict["is_removed"] == 1: 
                    cursor.execute("""
                        UPDATE Johnny_docInBox
                        SET is_removed = 0
                        WHERE doc_id = ? AND box_id = ?
                    """, (doc_id, box_id))
                    conn.commit()
                else:
                    # หาก box_id มีค่าอยู่แล้ว ให้แสดงข้อผิดพลาด
                    raise ValueError(f"เอกสารเลขนี้ {doc_id} มีอยู่ในกล่อง {row_dict['box_id']} แล้ว")
            else:
                cursor.execute("""
                    INSERT INTO Johnny_docInBox (id, doc_id, box_id, is_removed)
                    VALUES (?, ?, ?, ?)
                """, (id, doc_id, box_id, 0))  # is_removed = 0 หมายถึงยังไม่ถูกเอาออก
                conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def remove_docInBox(cls, doc_id, box_id, user_email):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Johnny_docInBox WHERE doc_id = ?", (doc_id,))
            row = cursor.fetchone()
            if row:
                row_dict = dict(zip([column[0] for column in cursor.description], row))
                # แถวที่ select มาแล้ว ตรวจสอบค่า box_id
                if row_dict["is_removed"] == 1:  # ตรวจสอบว่า box_id ถูกเอาออกไปแล้ว
                    raise ValueError(f"เอกสารเลขนี้ {doc_id} ถูกเอาออกจากกล่องไปแล้ว") 
                elif row_dict["box_id"] != box_id:
                    raise ValueError(f"เอกสารเลขนี้ {doc_id} ไม่ได้อยู่ในกล่อง {box_id}")
                else:
                    # DELETE FROM Johnny_docInBox WHERE doc_id = ? AND box_id = ?
                    cursor.execute("""
                        UPDATE Johnny_docInBox SET is_removed = ? WHERE doc_id = ? AND box_id = ?
                    """, (True,doc_id, box_id))
                    cursor.execute("""
                        UPDATE Johnny_doc SET remove_at = ?, remove_by = ? WHERE doc_id = ?
                    """, (datetime.now()+ timedelta(hours=7), user_email, doc_id))
                    conn.commit()
            else:
                raise ValueError(f"เอกสารเลขนี้ {doc_id} ยังไม่เคยถูกจัดเก็บ")
        finally:
            cursor.close()
            conn.close()

class Search:
    @classmethod
    def search_boxes(cls, box_id=None, box_year=None, boxtype_id=None, location=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # สร้าง SQL query พื้นฐาน
            query = """
                SELECT [box_id]
                    ,[box_year]
                    ,[boxtype_id]
                    ,[box_number]
                    ,[update_at]
                    ,[update_by]
                    ,[create_at]
                    ,[create_by]
                    ,Johnny_location.location_name AS location
                FROM [dbo].[Johnny_box]
                LEFT JOIN [dbo].[Johnny_location] ON Johnny_box.location_id = Johnny_location.location_id
                WHERE 1=1
            """

            # เพิ่มเงื่อนไขใน query ตามพารามิเตอร์ที่ได้รับ
            if box_id:
                query += f" AND box_id LIKE '%{box_id}%'"
            if box_year:
                query += f" AND box_year = '{box_year}'"
            if boxtype_id:
                query += f" AND boxtype_id = '{boxtype_id}'"
            if location:
                query += f" AND Johnny_location.name LIKE '%{location}%'"

            cursor.execute(query)  # รัน query ที่สร้างขึ้น
            rows = cursor.fetchall()
            if not rows:
                return []  # หากไม่มีข้อมูล ให้คืนค่าเป็น list ว่างๆ

            columns = [column[0] for column in cursor.description]


            def convert_datetime(value):
                if isinstance(value, datetime):
                    return value.isoformat()  # หรือใช้ str(value) ก็ได้
                return value
            
            # แปลงแต่ละแถวให้เป็น dictionary และแปลง datetime ให้เป็น string
            result = [dict(zip(columns, [convert_datetime(value) for value in row])) for row in rows]
            return result
        except Exception as e:
            print(f"Database error: {str(e)}")  # Add logging
            raise  # Re-raise the exception to be caught by the controller
        finally:
            cursor.close()
            conn.close()

    # @classmethod
    # def search_documents(cls, doc_id=None, doc_year=None, doctype_id=None, location=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # เริ่มจาก query พื้นฐาน
            query = """
                SELECT doc.doc_id
                    ,doc.doc_year
                    ,doc.doctype_id
                    ,doc.doc_number
                    ,doc.remove_at
                    ,doc.remove_by
                    ,doc.store_at
                    ,doc.store_by
                    ,docinbox.box_id
                    ,box.box_year
                    ,box.boxtype_id
                    ,box.box_close
                    ,box.location
                FROM [dbo].[Johnny_doc] doc
                LEFT JOIN [dbo].[Johnny_docInBox] docinbox ON doc.doc_id = docinbox.doc_id
                LEFT JOIN [dbo].[Johnny_box] box ON docinbox.box_id = box.box_id
                WHERE 1=1
            """

            # เพิ่มเงื่อนไข
            if doc_id:
                query += f" AND doc.doc_id LIKE '%{doc_id}%'"
            if doc_year:
                query += f" AND doc.doc_year = '{doc_year}'"
            if doctype_id:
                query += f" AND doc.doctype_id = '{doctype_id}'"
            if location:
                query += f" AND box.location LIKE '%{location}%'"

            # ส่ง query ไป execute
            cursor.execute(query)

            rows = cursor.fetchall()  # ใช้ fetchall เพื่อดึงข้อมูลทั้งหมด
            if not rows:
                return []  # หากไม่มีข้อมูล ให้คืนค่าเป็น list ว่างๆ

            columns = [column[0] for column in cursor.description]


            def convert_datetime(value):
                if isinstance(value, datetime):
                    return value.isoformat()  # หรือใช้ str(value) ก็ได้
                return value
            
            # แปลงแต่ละแถวให้เป็น dictionary และแปลง datetime ให้เป็น string
            result = [dict(zip(columns, [convert_datetime(value) for value in row])) for row in rows]
            return result
        except Exception as e:
            print(f"Database error: {str(e)}")  # Add logging
            raise  # Re-raise the exception to be caught by the controller
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def search_documents(cls, doc_ids=None, doc_year=None, doctype_id=None, location=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = """
                SELECT doc.doc_id
                    ,doc.doc_year
                    ,doc.doctype_id
                    ,doc.doc_number
                    ,doc.remove_at
                    ,doc.remove_by
                    ,doc.store_at
                    ,doc.store_by
                    ,docinbox.box_id
                    ,docinbox.is_removed
                    ,box.box_year
                    ,box.boxtype_id
                    ,location.location_name AS location
                FROM [dbo].[Johnny_doc] doc
                LEFT JOIN [dbo].[Johnny_docInBox] docinbox ON doc.doc_id = docinbox.doc_id
                LEFT JOIN [dbo].[Johnny_box] box ON docinbox.box_id = box.box_id
                LEFT JOIN [dbo].[Johnny_location] location ON box.location_id = location.location_id
                WHERE 1=1
            """

            # รองรับหลาย id
            if doc_ids:
                if isinstance(doc_ids, list):
                    placeholders = ','.join(['?'] * len(doc_ids))
                    query += f" AND doc.doc_id IN ({placeholders})"
                else:
                    query += f" AND doc.doc_id LIKE '%{doc_ids}%'"

            if doc_year:
                query += f" AND doc.doc_year = '{doc_year}'"
            if doctype_id:
                query += f" AND doc.doctype_id = '{doctype_id}'"
            if location:
                query += f" AND location.location_name LIKE '%{location}%'"

            if isinstance(doc_ids, list):
                cursor.execute(query, tuple(doc_ids))
            else:
                cursor.execute(query)

            rows = cursor.fetchall()
            if not rows:
                return []

            columns = [column[0] for column in cursor.description]

            def convert_datetime(value):
                if isinstance(value, datetime):
                    return value.isoformat()
                return value

            result = [dict(zip(columns, [convert_datetime(value) for value in row])) for row in rows]
            return result

        except Exception as e:
            print(f"Database error: {str(e)}")
            raise
        finally:
            cursor.close()
            conn.close()
# class Authentication:
#     @classmethod
#     def check_user_exists(cls, user_email):
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         try:
#             cursor.execute("SELECT * FROM ThothUserQuota WHERE UserEmail = ?", (user_email,))
#             rows = cursor.fetchall()
#             return len(rows) > 0
#         finally:
#             cursor.close()
#             conn.close()
#
#     @classmethod
#     def check_login_attempt(user_email):
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         try:
#             cursor.execute(f"SELECT TOP 1 * FROM ThothLoginLog WHERE UserEmail = ? ORDER BY LastLogin DESC", user_email)
#             row = cursor.fetchone()
#             if not row:
#                 return True
#             if datetime.datetime.now() - row[2] < datetime.timedelta(minutes=5) and row[4] >= 3 and row[3] == 0:
#                 return False
#             return True
#         finally:
#             cursor.close()
#             conn.close()

#     @classmethod
#     def insert_data_user_info(data): # when login first time
#         conn = get_db_connection()
#         cursor = conn.cursor()
#         try:
#             # insert data
#             cursor.execute(f"INSERT INTO ThothUserQuota (UserEmail, Tier, DailyFilesSent, DailyImagesGenerated, DailyInputTokenSum, DailyOutputTokenSum, LastUpdated) VALUES (?, ?, ?, ?, ?, ?, ?)", data)
#             # write log to insert_log.txt
#             with open('insert_log.txt', 'a', encoding='utf-8') as f:
#                 f.write('UserEmail: ' + data[0] + ', ')
#                 f.write('Tier: ' + str(data[1]) + ', ')
#                 f.write('DailyFilesSent: ' + str(data[2]) + ', ')
#                 f.write('DailyImagesGenerated: ' + str(data[3]) + ', ')
#                 f.write('DailyInputTokenSum: ' + str(data[4]) + ', ')
#                 f.write('DailyOutputTokenSum: ' + str(data[5]) + ', ')
#                 f.write('LastUpdated: ' + str(data[6]) + '\n')
#             conn.commit()
#         finally:
#             cursor.close()
#             conn.close()

# def log_error_to_file(error_message):
#     with open('error_log.txt', 'a') as f:
#         f.write(f"{str(datetime.datetime.now())} - ERROR - {error_message}\n")
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
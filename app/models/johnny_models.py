from datetime import datetime,timedelta, date
from decimal import Decimal
from uuid import uuid4
import pytz
from app.db import get_db_connection

# ฟังก์ชันสำหรับได้เวลาปัจจุบันใน timezone ประเทศไทย
def get_current_datetime():
    """ได้เวลาปัจจุบันใน timezone ประเทศไทย (UTC+7)"""
    thailand_tz = pytz.timezone('Asia/Bangkok')
    return datetime.now(thailand_tz)
from collections import OrderedDict, defaultdict


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
            """, (boxtype_id, boxtype_name, boxtype_shortname, get_current_datetime()))
            cursor.execute("""
                INSERT INTO Johnny_docType (doctype_id, doctype_name, doctype_shortname, created_at)
                VALUES (?, ?, ?, ?)
            """, (boxtype_id, boxtype_name, boxtype_shortname, get_current_datetime()))
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
            """, (boxtype_name, boxtype_shortname, get_current_datetime(), boxtype_id))
            cursor.execute("""
                UPDATE Johnny_docType 
                    SET doctype_name = ?, doctype_shortname = ?, created_at = ? 
                    WHERE doctype_id = ?
            """, (boxtype_name, boxtype_shortname, get_current_datetime(), boxtype_id))
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
            """, ( location_name, get_current_datetime()))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def update_location(cls,location_id, location_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Johnny_location 
                    SET location_name = ?, created_at = ?
                    WHERE location_id = ?
            """, (location_name, get_current_datetime(), location_id))
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
            """, (box_id, box_type, box_year, next_box_number, create_by, get_current_datetime(),location))
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
            #     """, (status, get_current_datetime(), user_email, box_number))
            #     conn.commit()

            # ตรวจสอบว่า box_action เป็น RELOCATE
            if box_action == "RELOCATE":
                # การอัพเดตเมื่อ box_action เป็น RELOCATE
                cursor.execute("""
                    UPDATE Johnny_box 
                    SET location_id = ?, update_at = ?, update_by = ? 
                    WHERE box_id = ?
                """, (location, get_current_datetime(), user_email, box_number))
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
                """, (get_current_datetime()+ timedelta(hours=7), store_by, doc_id))
            else:
                cursor.execute("""
                    INSERT INTO Johnny_doc (doc_id, doctype_id, doc_year, doc_number, store_by, store_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (doc_id, doctype_id, doc_year, doc_number, store_by, get_current_datetime()))
            conn.commit()
            return doc_id
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def bulk_create_docs(cls, documents_data, store_by):
        """
        Bulk create multiple documents efficiently
        documents_data: list of dict with keys: doc_year, doctype_id, doc_number
        """
        if not documents_data:
            return []
            
        conn = get_db_connection()
        cursor = conn.cursor()
        created_docs = []
        
        try:
            # Prepare bulk data
            insert_data = []
            update_data = []
            
            for doc_data in documents_data:
                doc_year = doc_data['doc_year']
                doctype_id = doc_data['doctype_id'] 
                doc_number = doc_data['doc_number']
                doc_id = f"{doc_year}{doc_number}"
                
                # Check if document exists
                cursor.execute("SELECT doc_id FROM Johnny_doc WHERE doc_id = ?", (doc_id,))
                existing_doc = cursor.fetchone()
                
                if existing_doc:
                    update_data.append((get_current_datetime() + timedelta(hours=7), store_by, doc_id))
                else:
                    insert_data.append((doc_id, doctype_id, doc_year, doc_number, store_by, get_current_datetime()))
                
                created_docs.append(doc_id)
            
            # Bulk insert new documents
            if insert_data:
                cursor.executemany("""
                    INSERT INTO Johnny_doc (doc_id, doctype_id, doc_year, doc_number, store_by, store_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, insert_data)
            
            # Bulk update existing documents
            if update_data:
                cursor.executemany("""
                    UPDATE Johnny_doc 
                    SET store_at = ?, store_by = ? 
                    WHERE doc_id = ?
                """, update_data)
            
            conn.commit()
            return created_docs
            
        except Exception as e:
            conn.rollback()
            raise e
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
    def get_doc_by_id(cls, doc_id):
        """Get document info by doc_id"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Johnny_docInBox WHERE doc_id = ?", (doc_id,))
            row = cursor.fetchone()
            if row:
                return dict(zip([column[0] for column in cursor.description], row))
            return None
        finally:
            cursor.close()
            conn.close()
    
    @classmethod
    def create_docInBox(cls, id, doc_id, box_id):
        """
        Create docInBox entry with improved error handling.
        Returns tuple: (success: bool, message: str)
        """
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
                    return (True, f"เอกสาร {doc_id} ถูกเปิดใช้งานในกล่อง {box_id} แล้ว")
                else:
                    # หาก box_id มีค่าอยู่แล้ว ให้คืนค่า error แทนที่จะ throw
                    return (False, f"เอกสารเลขนี้ {doc_id} มีอยู่ในกล่อง {row_dict['box_id']} แล้ว")
            else:
                cursor.execute("""
                    INSERT INTO Johnny_docInBox (id, doc_id, box_id, is_removed)
                    VALUES (?, ?, ?, ?)
                """, (id, doc_id, box_id, 0))  # is_removed = 0 หมายถึงยังไม่ถูกเอาออก
                conn.commit()
                return (True, f"เอกสาร {doc_id} ถูกเพิ่มเข้ากล่อง {box_id} เรียบร้อยแล้ว")
        except Exception as e:
            return (False, f"เกิดข้อผิดพลาดในการเพิ่มเอกสาร {doc_id}: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def bulk_create_docInBox(cls, documents_data, box_id):
        """
        Bulk create multiple DocInBox entries efficiently
        documents_data: list of dict with keys: id, doc_id
        """
        if not documents_data:
            return []
            
        conn = get_db_connection()
        cursor = conn.cursor()
        created_entries = []
        errors = []
        
        try:
            for doc_data in documents_data:
                try:
                    # Check if document already exists
                    cursor.execute("SELECT * FROM Johnny_docInBox WHERE doc_id = ?", (doc_data['doc_id'],))
                    row = cursor.fetchone()
                    
                    if row:
                        row_dict = dict(zip([column[0] for column in cursor.description], row))
                        if row_dict["is_removed"] == 1:
                            # Reactivate the document
                            cursor.execute("""
                                UPDATE Johnny_docInBox
                                SET is_removed = 0
                                WHERE doc_id = ? AND box_id = ?
                            """, (doc_data['doc_id'], box_id))
                            conn.commit()
                            created_entries.append({
                                'id': doc_data['id'],
                                'doc_id': doc_data['doc_id'],
                                'box_id': box_id,
                                'status': 'reactivated'
                            })
                        else:
                            errors.append({
                                'doc_id': doc_data['doc_id'],
                                'error': f"เอกสารเลขนี้ {doc_data['doc_id']} มีอยู่ในกล่อง {row_dict['box_id']} แล้ว"
                            })
                    else:
                        # Create new entry
                        cursor.execute("""
                            INSERT INTO Johnny_docInBox (id, doc_id, box_id, is_removed)
                            VALUES (?, ?, ?, ?)
                        """, (doc_data['id'], doc_data['doc_id'], box_id, 0))
                        conn.commit()
                        created_entries.append({
                            'id': doc_data['id'],
                            'doc_id': doc_data['doc_id'],
                            'box_id': box_id,
                            'status': 'created'
                        })
                        
                except Exception as e:
                    errors.append({
                        'doc_id': doc_data['doc_id'],
                        'error': str(e)
                    })
                    
        except Exception as e:
            conn.rollback()
            raise  # Re-raise the exception to be caught by the controller
        finally:
            cursor.close()
            conn.close()
            
        return {
            'created_entries': created_entries,
            'errors': errors
        }

    @classmethod
    def remove_docInBox(cls, doc_id, box_id, user_email):
        """
        Remove document from box with improved error handling.
        Returns tuple: (success: bool, message: str)
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM Johnny_docInBox WHERE doc_id = ?", (doc_id,))
            row = cursor.fetchone()
            if row:
                row_dict = dict(zip([column[0] for column in cursor.description], row))
                # แถวที่ select มาแล้ว ตรวจสอบค่า box_id
                if row_dict["is_removed"] == 1:  # ตรวจสอบว่า box_id ถูกเอาออกไปแล้ว
                    return (False, f"เอกสารเลขนี้ {doc_id} ถูกเอาออกจากกล่องไปแล้ว")
                elif row_dict["box_id"] != box_id:
                    return (False, f"เอกสารเลขนี้ {doc_id} ไม่ได้อยู่ในกล่อง {box_id}")
                else:
                    # DELETE FROM Johnny_docInBox WHERE doc_id = ? AND box_id = ?
                    cursor.execute("""
                        UPDATE Johnny_docInBox SET is_removed = ? WHERE doc_id = ? AND box_id = ?
                    """, (True,doc_id, box_id))
                    cursor.execute("""
                        UPDATE Johnny_doc SET remove_at = ?, remove_by = ? WHERE doc_id = ?
                    """, (get_current_datetime()+ timedelta(hours=7), user_email, doc_id))
                    conn.commit()
                    return (True, f"เอกสาร {doc_id} ถูกเอาออกจากกล่อง {box_id} เรียบร้อยแล้ว")
            else:
                return (False, f"เอกสารเลขนี้ {doc_id} ยังไม่เคยถูกจัดเก็บ")
        except Exception as e:
            return (False, f"เกิดข้อผิดพลาดในการเอาออกเอกสาร {doc_id}: {str(e)}")
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def create_approve_pickup(cls,approval_id, requester_email, approver_email, approval_detail):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Johnny_approvalRequest (approval_id, requester_email, approver_email, approval_detail, requester_request_at, approval_status, approval_response)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (approval_id, requester_email, approver_email, approval_detail, get_current_datetime(), 'pending', None))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_pickup_request(cls, approval_id, requester_email, approver_email, status):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # cursor.execute("SELECT * FROM Johnny_approvalRequest WHERE requester_email = ? AND approver_email = ? AND approval_status = ?", (requester_email, approver_email, status))
            params = []
            query = """
                SELECT * FROM Johnny_approvalRequest
                WHERE 1=1
            """
            if approval_id:
                query += " AND approval_id = ?"
                params.append(approval_id)

            if requester_email:
                query += " AND requester_email = ?"
                params.append(requester_email)

            if approver_email:
                query += " AND approver_email = ?"
                params.append(approver_email)

            if status:
                query += " AND approval_status = ?"
                params.append(status)

            rows =cursor.execute(query, params)
            if not rows:
                return []
            return [map_row_to_dict(cursor, row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def update_approval_status(cls, approval_id, approval_status, approver_comment, approval_response=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            print(f"=== DEBUG: update_approval_status ===")
            print(f"approval_id: {approval_id}")
            print(f"approval_status: {approval_status}")
            print(f"approver_comment: {approver_comment}")
            print(f"approval_response type: {type(approval_response)}")
            print(f"approval_response length: {len(approval_response) if approval_response else 'None'}")
            print(f"approval_response preview: {approval_response[:200] if approval_response else 'None'}...")
            
            cursor.execute("""
                UPDATE Johnny_approvalRequest 
                SET approval_status = ?, approver_action_at = ?, approver_comment = ?, approval_response = ?
                WHERE approval_id = ?
            """, (approval_status, get_current_datetime(), approver_comment, approval_response, approval_id))
            
            # Check if any rows were affected
            rows_affected = cursor.rowcount
            print(f"Rows affected by UPDATE: {rows_affected}")
            
            conn.commit()
            print("=== DEBUG: Commit successful ===")
            
            # Verify the update by reading back the data
            cursor.execute("SELECT approval_response FROM Johnny_approvalRequest WHERE approval_id = ?", (approval_id,))
            result = cursor.fetchone()
            print(f"Verification - approval_response in DB: {result[0] if result and result[0] else 'NULL'}")
            
        except Exception as e:
            print(f"=== DEBUG: Error in update_approval_status ===")
            print(f"Error: {str(e)}")
            print(f"Error type: {type(e)}")
            raise e
        finally:
            cursor.close()
            conn.close()
    

class Search:
    @classmethod
    def search_boxes(cls, box_id=None, box_year=None, boxtype_id=None, location=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # สร้าง SQL query พื้นฐาน - รวมเอกสารในกล่องด้วย
            query = """
                SELECT doc.doc_id
                    ,doc.doc_year
                    ,doc.doctype_id
                    ,doc.doc_number
                    ,doc.remove_at
                    ,doc.remove_by
                    ,doc.store_at
                    ,doc.store_by
                    ,box.box_id
                    ,docinbox.is_removed
                    ,box.box_year
                    ,box.boxtype_id
                    ,box.box_number
                    ,box.update_at
                    ,box.update_by
                    ,box.create_at
                    ,box.create_by
                    ,location.location_name AS location
                FROM [dbo].[Johnny_box] box
                LEFT JOIN [dbo].[Johnny_location] location ON box.location_id = location.location_id
                LEFT JOIN [dbo].[Johnny_docInBox] docinbox ON box.box_id = docinbox.box_id AND docinbox.is_removed = 0
                LEFT JOIN [dbo].[Johnny_doc] doc ON docinbox.doc_id = doc.doc_id
                WHERE 1=1
            """

            # เพิ่มเงื่อนไขใน query ตามพารามิเตอร์ที่ได้รับ
            if box_id:
                if isinstance(box_id, list):
                    placeholders = ','.join(['?'] * len(box_id))
                    query += f" AND box.box_id IN ({placeholders})"
                else:
                    query += f" AND box.box_id LIKE '%{box_id}%'"
            if box_year:
                query += f" AND box.box_year = '{box_year}'"
            if boxtype_id:
                query += f" AND box.boxtype_id = '{boxtype_id}'"
            if location:
                query += f" AND location.location_name LIKE '%{location}%'"

            # เรียงลำดับตาม box_id และ doc_id
            query += " ORDER BY box.box_id, doc.doc_id"

            if isinstance(box_id, list):
                cursor.execute(query, tuple(box_id))
            else:
                cursor.execute(query)

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

    @classmethod
    def search_boxes_without_documents(cls, box_id=None, box_year=None, boxtype_id=None, location=None):
        """ค้นหากล่องที่ไม่มีเอกสาร"""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # สร้าง SQL query สำหรับกล่องที่ไม่มีเอกสาร
            query = """
                SELECT box.box_id
                    ,box.box_year
                    ,box.boxtype_id
                    ,box.box_number
                    ,box.update_at
                    ,box.update_by
                    ,box.create_at
                    ,box.create_by
                    ,location.location_name AS location
                FROM [dbo].[Johnny_box] box
                LEFT JOIN [dbo].[Johnny_location] location ON box.location_id = location.location_id
                LEFT JOIN [dbo].[Johnny_docInBox] docinbox ON box.box_id = docinbox.box_id AND docinbox.is_removed = 0
                WHERE docinbox.box_id IS NULL
            """

            # เพิ่มเงื่อนไขใน query ตามพารามิเตอร์ที่ได้รับ
            if box_id:
                if isinstance(box_id, list):
                    placeholders = ','.join(['?'] * len(box_id))
                    query += f" AND box.box_id IN ({placeholders})"
                else:
                    query += f" AND box.box_id LIKE '%{box_id}%'"
            if box_year:
                query += f" AND box.box_year = '{box_year}'"
            if boxtype_id:
                query += f" AND box.boxtype_id = '{boxtype_id}'"
            if location:
                query += f" AND location.location_name LIKE '%{location}%'"

            # เรียงลำดับตาม box_id
            query += " ORDER BY box.box_id"

            if isinstance(box_id, list):
                cursor.execute(query, tuple(box_id))
            else:
                cursor.execute(query)

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

class UserManagement:
    @classmethod
    def get_user(cls, user_email):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # cursor.execute("SELECT * FROM Johnny_approvalRequest WHERE requester_email = ? AND approver_email = ? AND approval_status = ?", (requester_email, approver_email, status))
            params = []
            query = """
                SELECT * FROM Johnny_user
                WHERE 1=1
            """
            if user_email:
                query += " AND user_email = ?"
                params.append(user_email)

            rows =cursor.execute(query, params)
            if not rows:
                return []
            return [map_row_to_dict(cursor, row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    # @classmethod
    # def get_approver_by_email(cls, user_email):
    #     conn = get_db_connection()
    #     cursor = conn.cursor()
    #     try:
    #         cursor.execute("SELECT is_approver FROM Johnny_user WHERE user_email = ?", (user_email,))
    #         row = cursor.fetchone()
    #         if row:
    #             return row  # Return the raw row or map to an object
    #         return None
    #     finally:
    #         cursor.close()
    #         conn.close()

    @classmethod
    def get_approver(cls):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = """
                SELECT user_email, user_name, is_approver, role_id FROM Johnny_user
                WHERE is_approver = 1
            """

            rows =cursor.execute(query)
            if not rows:
                return []
            return [map_row_to_dict(cursor, row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_all_users(cls):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = """
                SELECT u.user_email, u.user_name, u.role_id, u.is_approver, u.last_login,
                       r.role_name
                FROM Johnny_user u
                LEFT JOIN Johnny_role r ON u.role_id = r.role_id
                ORDER BY u.user_email
            """

            cursor.execute(query)
            rows = cursor.fetchall()
            if not rows:
                return []
            return [map_row_to_dict(cursor, row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def create_user(cls, user_email, user_name, role_id, is_approver):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if user already exists
            cursor.execute("SELECT user_email FROM Johnny_user WHERE user_email = ?", (user_email,))
            if cursor.fetchone():
                raise ValueError("User with this email already exists")
            
            cursor.execute("""
                INSERT INTO Johnny_user (user_email, user_name, role_id, is_approver, last_login)
                VALUES (?, ?, ?, ?, ?)
            """, (user_email, user_name, role_id, is_approver, None))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def update_user(cls, user_email, user_name=None, role_id=None, is_approver=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if user exists
            cursor.execute("SELECT user_email FROM Johnny_user WHERE user_email = ?", (user_email,))
            if not cursor.fetchone():
                raise ValueError("User not found")
            
            # Build dynamic update query
            updates = []
            params = []
            
            if user_name is not None:
                updates.append("user_name = ?")
                params.append(user_name)
            
            if role_id is not None:
                updates.append("role_id = ?")
                params.append(role_id)
            
            if is_approver is not None:
                updates.append("is_approver = ?")
                params.append(is_approver)
            
            if updates:
                params.append(user_email)
                query = f"UPDATE Johnny_user SET {', '.join(updates)} WHERE user_email = ?"
                cursor.execute(query, params)
                conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def delete_user(cls, user_email):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if user exists
            cursor.execute("SELECT user_email FROM Johnny_user WHERE user_email = ?", (user_email,))
            if not cursor.fetchone():
                raise ValueError("User not found")
            
            cursor.execute("DELETE FROM Johnny_user WHERE user_email = ?", (user_email,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_all_roles(cls):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            query = """
                SELECT r.role_id, r.role_name, r.allow_create, r.allow_change, r.allow_pickup,
                       r.allow_setting, r.allow_report, r.allow_user_manage,
                       COUNT(u.user_email) as user_count
                FROM Johnny_role r
                LEFT JOIN Johnny_user u ON r.role_id = u.role_id
                GROUP BY r.role_id, r.role_name, r.allow_create, r.allow_change, r.allow_pickup,
                         r.allow_setting, r.allow_report, r.allow_user_manage
                ORDER BY r.role_id
            """

            cursor.execute(query)
            rows = cursor.fetchall()
            if not rows:
                return []
            return [map_row_to_dict(cursor, row) for row in rows]
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def create_role(cls, role_name, allow_create, allow_change, allow_pickup, allow_setting, allow_report, allow_user_manage):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if role already exists
            cursor.execute("SELECT role_name FROM Johnny_role WHERE role_name = ?", (role_name,))
            if cursor.fetchone():
                raise ValueError("Role with this name already exists")
            
            # Insert new role without specifying role_id (let identity column handle it)
            cursor.execute("""
                INSERT INTO Johnny_role (role_name, allow_create, allow_change, allow_pickup, 
                                       allow_setting, allow_report, allow_user_manage)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (role_name, allow_create, allow_change, allow_pickup, 
                  allow_setting, allow_report, allow_user_manage))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def update_role(cls, role_id, role_name=None, allow_create=None, allow_change=None, allow_pickup=None, 
                   allow_setting=None, allow_report=None, allow_user_manage=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if role exists
            cursor.execute("SELECT role_id FROM Johnny_role WHERE role_id = ?", (role_id,))
            if not cursor.fetchone():
                raise ValueError("Role not found")
            
            # Build dynamic update query
            updates = []
            params = []
            
            if role_name is not None:
                updates.append("role_name = ?")
                params.append(role_name)
            
            if allow_create is not None:
                updates.append("allow_create = ?")
                params.append(allow_create)
            
            if allow_change is not None:
                updates.append("allow_change = ?")
                params.append(allow_change)
            
            if allow_pickup is not None:
                updates.append("allow_pickup = ?")
                params.append(allow_pickup)
            
            if allow_setting is not None:
                updates.append("allow_setting = ?")
                params.append(allow_setting)
            
            if allow_report is not None:
                updates.append("allow_report = ?")
                params.append(allow_report)
            
            if allow_user_manage is not None:
                updates.append("allow_user_manage = ?")
                params.append(allow_user_manage)
            
            if updates:
                params.append(role_id)
                query = f"UPDATE Johnny_role SET {', '.join(updates)} WHERE role_id = ?"
                cursor.execute(query, params)
                conn.commit()
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def delete_role(cls, role_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Check if role exists
            cursor.execute("SELECT role_id FROM Johnny_role WHERE role_id = ?", (role_id,))
            if not cursor.fetchone():
                raise ValueError("Role not found")
            
            # Check if any users are using this role
            cursor.execute("SELECT COUNT(*) FROM Johnny_user WHERE role_id = ?", (role_id,))
            user_count = cursor.fetchone()[0]
            if user_count > 0:
                raise ValueError("Cannot delete role that is being used by users")
            
            cursor.execute("DELETE FROM Johnny_role WHERE role_id = ?", (role_id,))
            conn.commit()
        finally:
            cursor.close()
            conn.close()

class JohnnyReport:
    THAI_MONTH_ABBR = [
        "",
        "ม.ค.",
        "ก.พ.",
        "มี.ค.",
        "เม.ย.",
        "พ.ค.",
        "มิ.ย.",
        "ก.ค.",
        "ส.ค.",
        "ก.ย.",
        "ต.ค.",
        "พ.ย.",
        "ธ.ค.",
    ]

    @staticmethod
    def _safe_percentage(current, previous):
        previous_value = previous or 0
        current_value = current or 0
        if previous_value == 0:
            return 100.0 if current_value > 0 else 0.0
        try:
            return round(((current_value - previous_value) / previous_value) * 100, 2)
        except Exception:
            return 0.0

    @staticmethod
    def _serialize_datetime(value):
        if isinstance(value, datetime):
            return value.isoformat()
        return None

    @staticmethod
    def _month_sequence(months):
        months = max(1, months)
        today = get_current_datetime().date()
        year = today.year
        month = today.month
        sequence = []
        for _ in range(months):
            sequence.append((year, month))
            month -= 1
            if month == 0:
                month = 12
                year -= 1
        sequence.reverse()
        return sequence

    @staticmethod
    def _month_label(year, month):
        if 1 <= month <= 12:
            return f"{JohnnyReport.THAI_MONTH_ABBR[month]} {year}"
        return f"{month:02d}/{year}"

    @staticmethod
    def _period_key(year, month):
        return f"{year}-{month:02d}"

    @staticmethod
    def _get_month_range(sequence):
        first_year, first_month = sequence[0]
        last_year, last_month = sequence[-1]
        start_date = datetime(first_year, first_month, 1)
        if last_month == 12:
            end_date = datetime(last_year + 1, 1, 1)
        else:
            end_date = datetime(last_year, last_month + 1, 1)
        return start_date, end_date

    @classmethod
    def get_dashboard_summary(cls, months=6):
        conn = get_db_connection()
        if conn is None:
            return {}
        cursor = conn.cursor()
        try:
            summary = {}

            cursor.execute("SELECT COUNT(*) FROM Johnny_box")
            total_boxes_row = cursor.fetchone()
            summary["total_boxes"] = int(total_boxes_row[0]) if total_boxes_row and total_boxes_row[0] is not None else 0

            cursor.execute("SELECT COUNT(*) FROM Johnny_doc")
            total_docs_row = cursor.fetchone()
            summary["total_documents"] = int(total_docs_row[0]) if total_docs_row and total_docs_row[0] is not None else 0

            cursor.execute("SELECT COUNT(*) FROM Johnny_docInBox WHERE is_removed = 0")
            docs_in_storage_row = cursor.fetchone()
            summary["documents_in_storage"] = int(docs_in_storage_row[0]) if docs_in_storage_row and docs_in_storage_row[0] is not None else 0

            cursor.execute("SELECT COUNT(*) FROM Johnny_approvalRequest WHERE approval_status = 'pending'")
            pending_requests_row = cursor.fetchone()
            summary["pending_approvals"] = int(pending_requests_row[0]) if pending_requests_row and pending_requests_row[0] is not None else 0

            cursor.execute("SELECT COUNT(*) FROM Johnny_approvalRequest WHERE approval_status = 'approved' AND approver_action_at >= DATEADD(DAY, -30, GETDATE())")
            approvals_30_row = cursor.fetchone()
            summary["approvals_last_30_days"] = int(approvals_30_row[0]) if approvals_30_row and approvals_30_row[0] is not None else 0

            cursor.execute("SELECT COUNT(*) FROM Johnny_user")
            users_total_row = cursor.fetchone()
            summary["users_total"] = int(users_total_row[0]) if users_total_row and users_total_row[0] is not None else 0

            cursor.execute(
                """
                SELECT COUNT(*) FROM Johnny_user
                WHERE last_login IS NOT NULL
                  AND last_login >= DATEADD(DAY, -30, GETDATE())
                """
            )
            active_users_row = cursor.fetchone()
            summary["active_users_30d"] = int(active_users_row[0]) if active_users_row and active_users_row[0] is not None else 0

            cursor.execute(
                """
                SELECT
                    SUM(CASE WHEN YEAR(create_at) = YEAR(GETDATE()) AND MONTH(create_at) = MONTH(GETDATE()) THEN 1 ELSE 0 END) AS current_month,
                    SUM(CASE WHEN YEAR(create_at) = YEAR(DATEADD(MONTH, -1, GETDATE())) AND MONTH(create_at) = MONTH(DATEADD(MONTH, -1, GETDATE())) THEN 1 ELSE 0 END) AS previous_month
                FROM Johnny_box
                """
            )
            box_growth_row = cursor.fetchone()
            current_boxes = int(box_growth_row[0]) if box_growth_row and box_growth_row[0] is not None else 0
            previous_boxes = int(box_growth_row[1]) if box_growth_row and box_growth_row[1] is not None else 0
            summary["monthly_box_growth"] = {
                "current": current_boxes,
                "previous": previous_boxes,
                "percentage": cls._safe_percentage(current_boxes, previous_boxes),
            }

            cursor.execute(
                """
                SELECT
                    SUM(CASE WHEN store_at IS NOT NULL AND YEAR(store_at) = YEAR(GETDATE()) AND MONTH(store_at) = MONTH(GETDATE()) THEN 1 ELSE 0 END) AS current_month,
                    SUM(CASE WHEN store_at IS NOT NULL AND YEAR(store_at) = YEAR(DATEADD(MONTH, -1, GETDATE())) AND MONTH(store_at) = MONTH(DATEADD(MONTH, -1, GETDATE())) THEN 1 ELSE 0 END) AS previous_month
                FROM Johnny_doc
                """
            )
            doc_growth_row = cursor.fetchone()
            current_docs = int(doc_growth_row[0]) if doc_growth_row and doc_growth_row[0] is not None else 0
            previous_docs = int(doc_growth_row[1]) if doc_growth_row and doc_growth_row[1] is not None else 0
            summary["monthly_document_growth"] = {
                "current": current_docs,
                "previous": previous_docs,
                "percentage": cls._safe_percentage(current_docs, previous_docs),
            }

            summary["generated_at"] = cls._serialize_datetime(get_current_datetime())
            return summary
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_dashboard_trends(cls, months=6):
        sequence = cls._month_sequence(months)
        if not sequence:
            return {"boxes": [], "documents": [], "approvals": []}

        start_date, end_date = cls._get_month_range(sequence)

        conn = get_db_connection()
        if conn is None:
            return {"boxes": [], "documents": [], "approvals": []}
        cursor = conn.cursor()
        try:
            boxes_counts = defaultdict(int)
            box_rows = cursor.execute(
                """
                SELECT YEAR(create_at) AS year, MONTH(create_at) AS month, COUNT(*) AS total
                FROM Johnny_box
                WHERE create_at IS NOT NULL
                  AND create_at >= ?
                  AND create_at < ?
                GROUP BY YEAR(create_at), MONTH(create_at)
                """,
                (start_date, end_date),
            ).fetchall()
            for row in box_rows:
                year = int(row[0])
                month = int(row[1])
                count = int(row[2]) if row[2] is not None else 0
                boxes_counts[(year, month)] = count

            documents_counts = defaultdict(int)
            doc_rows = cursor.execute(
                """
                SELECT YEAR(store_at) AS year, MONTH(store_at) AS month, COUNT(*) AS total
                FROM Johnny_doc
                WHERE store_at IS NOT NULL
                  AND store_at >= ?
                  AND store_at < ?
                GROUP BY YEAR(store_at), MONTH(store_at)
                """,
                (start_date, end_date),
            ).fetchall()
            for row in doc_rows:
                year = int(row[0])
                month = int(row[1])
                count = int(row[2]) if row[2] is not None else 0
                documents_counts[(year, month)] = count

            approval_request_counts = defaultdict(int)
            approval_request_rows = cursor.execute(
                """
                SELECT YEAR(requester_request_at) AS year, MONTH(requester_request_at) AS month, COUNT(*) AS total
                FROM Johnny_approvalRequest
                WHERE requester_request_at IS NOT NULL
                  AND requester_request_at >= ?
                  AND requester_request_at < ?
                GROUP BY YEAR(requester_request_at), MONTH(requester_request_at)
                """,
                (start_date, end_date),
            ).fetchall()
            for row in approval_request_rows:
                year = int(row[0])
                month = int(row[1])
                count = int(row[2]) if row[2] is not None else 0
                approval_request_counts[(year, month)] = count

            approval_action_counts = defaultdict(lambda: {"approved": 0, "rejected": 0, "other": 0})
            approval_action_rows = cursor.execute(
                """
                SELECT YEAR(approver_action_at) AS year,
                       MONTH(approver_action_at) AS month,
                       approval_status,
                       COUNT(*) AS total
                FROM Johnny_approvalRequest
                WHERE approver_action_at IS NOT NULL
                  AND approver_action_at >= ?
                  AND approver_action_at < ?
                GROUP BY YEAR(approver_action_at), MONTH(approver_action_at), approval_status
                """,
                (start_date, end_date),
            ).fetchall()
            for row in approval_action_rows:
                year = int(row[0])
                month = int(row[1])
                status = (row[2] or "").lower()
                count = int(row[3]) if row[3] is not None else 0
                bucket = approval_action_counts[(year, month)]
                if status == "approved":
                    bucket["approved"] += count
                elif status == "rejected":
                    bucket["rejected"] += count
                else:
                    bucket["other"] += count

            boxes_trend = []
            documents_trend = []
            approvals_trend = []

            for year, month in sequence:
                period = cls._period_key(year, month)
                label = cls._month_label(year, month)

                boxes_trend.append(
                    {
                        "period": period,
                        "year": year,
                        "month": month,
                        "label": label,
                        "count": boxes_counts.get((year, month), 0),
                    }
                )

                documents_trend.append(
                    {
                        "period": period,
                        "year": year,
                        "month": month,
                        "label": label,
                        "count": documents_counts.get((year, month), 0),
                    }
                )

                approval_counts = approval_action_counts.get((year, month), {"approved": 0, "rejected": 0, "other": 0})
                approvals_trend.append(
                    {
                        "period": period,
                        "year": year,
                        "month": month,
                        "label": label,
                        "requested": approval_request_counts.get((year, month), 0),
                        "approved": approval_counts.get("approved", 0),
                        "rejected": approval_counts.get("rejected", 0),
                        "other": approval_counts.get("other", 0),
                    }
                )

            return {
                "boxes": boxes_trend,
                "documents": documents_trend,
                "approvals": approvals_trend,
            }
        finally:
            cursor.close()
            conn.close()

    @classmethod
    def get_recent_activity(cls, limit=10):
        limit = max(1, min(limit, 50))
        conn = get_db_connection()
        if conn is None:
            return []

        cursor = conn.cursor()
        try:
            events = []

            box_created_rows = cursor.execute(
                """
                SELECT TOP 50 box_id, create_by, create_at
                FROM Johnny_box
                WHERE create_at IS NOT NULL
                ORDER BY create_at DESC
                """
            ).fetchall()
            for row in box_created_rows:
                occurred_at = row[2]
                if not occurred_at:
                    continue
                actor = (row[1] or "").strip() or "ระบบ"
                reference_id = row[0]
                events.append(
                    {
                        "type": "box_created",
                        "reference_id": reference_id,
                        "actor": actor,
                        "occurred_at": occurred_at,
                        "title": f"สร้างกล่อง {reference_id}",
                        "description": f"{actor} สร้างกล่องใหม่",
                    }
                )

            box_updated_rows = cursor.execute(
                """
                SELECT TOP 50 box_id, update_by, update_at
                FROM Johnny_box
                WHERE update_at IS NOT NULL
                ORDER BY update_at DESC
                """
            ).fetchall()
            for row in box_updated_rows:
                occurred_at = row[2]
                if not occurred_at:
                    continue
                actor = (row[1] or "").strip() or "ระบบ"
                reference_id = row[0]
                events.append(
                    {
                        "type": "box_updated",
                        "reference_id": reference_id,
                        "actor": actor,
                        "occurred_at": occurred_at,
                        "title": f"อัปเดตกล่อง {reference_id}",
                        "description": f"{actor} อัปเดตข้อมูลกล่อง",
                    }
                )

            documents_stored_rows = cursor.execute(
                """
                SELECT TOP 50 d.doc_id, d.store_by, d.store_at, db.box_id
                FROM Johnny_doc d
                LEFT JOIN Johnny_docInBox db ON d.doc_id = db.doc_id AND db.is_removed = 0
                WHERE d.store_at IS NOT NULL
                ORDER BY d.store_at DESC
                """
            ).fetchall()
            for row in documents_stored_rows:
                occurred_at = row[2]
                if not occurred_at:
                    continue
                actor = (row[1] or "").strip() or "ระบบ"
                reference_id = row[0]
                box_id = row[3]
                if box_id:
                    description = f"{actor} จัดเก็บเอกสาร {reference_id} ในกล่อง {box_id}"
                else:
                    description = f"{actor} จัดเก็บเอกสาร {reference_id}"
                events.append(
                    {
                        "type": "document_stored",
                        "reference_id": reference_id,
                        "actor": actor,
                        "occurred_at": occurred_at,
                        "title": f"จัดเก็บเอกสาร {reference_id}",
                        "description": description,
                    }
                )

            documents_removed_rows = cursor.execute(
                """
                SELECT TOP 50 d.doc_id, d.remove_by, d.remove_at, db.box_id
                FROM Johnny_doc d
                LEFT JOIN Johnny_docInBox db ON d.doc_id = db.doc_id
                WHERE d.remove_at IS NOT NULL
                ORDER BY d.remove_at DESC
                """
            ).fetchall()
            for row in documents_removed_rows:
                occurred_at = row[2]
                if not occurred_at:
                    continue
                actor = (row[1] or "").strip() or "ระบบ"
                reference_id = row[0]
                box_id = row[3]
                if box_id:
                    description = f"{actor} นำเอกสาร {reference_id} ออกจากกล่อง {box_id}"
                else:
                    description = f"{actor} นำเอกสาร {reference_id} ออกจากคลัง"
                events.append(
                    {
                        "type": "document_removed",
                        "reference_id": reference_id,
                        "actor": actor,
                        "occurred_at": occurred_at,
                        "title": f"นำออกเอกสาร {reference_id}",
                        "description": description,
                    }
                )

            approval_requested_rows = cursor.execute(
                """
                SELECT TOP 50 approval_id, requester_email, requester_request_at
                FROM Johnny_approvalRequest
                WHERE requester_request_at IS NOT NULL
                ORDER BY requester_request_at DESC
                """
            ).fetchall()
            for row in approval_requested_rows:
                occurred_at = row[2]
                if not occurred_at:
                    continue
                actor = (row[1] or "").strip() or "ระบบ"
                reference_id = row[0]
                events.append(
                    {
                        "type": "approval_requested",
                        "reference_id": reference_id,
                        "actor": actor,
                        "occurred_at": occurred_at,
                        "title": f"คำขอเบิกเอกสาร {reference_id}",
                        "description": f"{actor} ส่งคำขอเบิกเอกสาร",
                    }
                )

            approval_action_rows = cursor.execute(
                """
                SELECT TOP 50 approval_id, approval_status, approver_email, approver_action_at
                FROM Johnny_approvalRequest
                WHERE approver_action_at IS NOT NULL
                ORDER BY approver_action_at DESC
                """
            ).fetchall()
            for row in approval_action_rows:
                occurred_at = row[3]
                if not occurred_at:
                    continue
                status = (row[1] or "").lower()
                if status == "approved":
                    status_label = "อนุมัติ"
                elif status == "rejected":
                    status_label = "ปฏิเสธ"
                else:
                    status_label = "ดำเนินการ"
                actor = (row[2] or "").strip() or "ระบบ"
                reference_id = row[0]
                events.append(
                    {
                        "type": f"approval_{status}",
                        "reference_id": reference_id,
                        "actor": actor,
                        "occurred_at": occurred_at,
                        "title": f"{status_label}คำขอ {reference_id}",
                        "description": f"{actor} {status_label.lower()}คำขอเบิกเอกสาร",
                    }
                )

            events.sort(key=lambda event: event["occurred_at"], reverse=True)

            serialised_events = []
            for event in events[:limit]:
                serialised_events.append(
                    {
                        "type": event["type"],
                        "reference_id": event["reference_id"],
                        "actor": event["actor"],
                        "occurred_at": cls._serialize_datetime(event["occurred_at"]),
                        "title": event["title"],
                        "description": event["description"],
                    }
                )

            return serialised_events
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


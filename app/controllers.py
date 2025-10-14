from datetime import datetime
from uuid import uuid4
from flask import json, jsonify, logging
from app.models import JohnnyBox, JohnnyDoc, DocInBox, Search, UserManagement
from app.db import get_db_connection
from app.config import Config
import base64
import re

class BoxController:
        
    def create_box(data):
        conn = get_db_connection()
        if conn is None:
            return {"message": "Failed to connect to the database"}, 500

        cursor = conn.cursor()
        try:
            box_type_code = data.get('box_type')  # ตอนนี้คาดว่าเป็นเลข เช่น "69", "212"
            box_year = data.get('box_year')
            create_amount = int(data.get('create_amount', 1))
            user_email = data.get('user_email')
            location = data.get('location')

            if not box_type_code or not box_year or not user_email or not location:
                return {"message": "Missing required fields"}, 400

            # แปลง box_type_code เป็น string ความยาว 3 หลัก เช่น "69" → "069"
            box_type = str(box_type_code).zfill(3)

            created_boxes = []
            for _ in range(create_amount):
                created_box = JohnnyBox.create_box(box_year, box_type, user_email, location)
                created_boxes.append(created_box)

            return {"message": "Boxes created successfully", "created_boxes": created_boxes}, 201

        except ValueError as e:
            return {"message": str(e)}, 400
        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        finally:
            cursor.close()
            conn.close()

    def update_box_status(data):
        boxes = data.get('box')
        box_action = data.get('box_action')
        user_email = data.get('user_email')
        location = data.get('location')

        if not boxes or not box_action or not user_email:
            return {"message": "Missing required fields"}, 400

        # manage_box_numbers = [box.get('ManageBoxNumber') for box in boxes]

        conn = get_db_connection()
        if conn is None:
            return {"message": "Failed to connect to the database"}, 500

        cursor = conn.cursor()
        try:
            for box_number in boxes:
                box_data = JohnnyBox.get_box_by_id(box_number)
                if not box_data:
                    return {"message": f"Box with ID {box_number} not found"}, 404
                JohnnyBox.update_box_status(box_action, user_email, box_number,location)

            return {"message": "Box status changed successfully", "changed_boxes": boxes}, 200

        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500
        finally:
            cursor.close()
            conn.close()

    def get_box_types():
        try:
            boxtypes = JohnnyBox.get_box_types()
            return {'data': boxtypes}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500
        
    def create_box_doc_types(data):
        boxtype_id = data.get('boxtype_id')
        boxtype_name = data.get('boxtype_name')
        boxtype_shortname = data.get('boxtype_shortname')
        try:
            JohnnyBox.create_box_doc_type(boxtype_id, boxtype_name, boxtype_shortname)
            return {"message": "BoxType create successfully"}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500
    
    def update_box_doc_types(data):
        boxtype_id = data.get('boxtype_id')
        boxtype_name = data.get('boxtype_name')
        boxtype_shortname = data.get('boxtype_shortname')
        try:
            JohnnyBox.update_box_doc_type(boxtype_id, boxtype_name, boxtype_shortname)
            return {"message": "BoxType update successfully"}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500
        
    def delete_box_doc_types(data):
        boxtype_id = data.get('boxtype_id')
        try:
            JohnnyBox.delete_box_doc_type(boxtype_id)
            return {"message": "BoxType delete successfully"}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500
        
    def get_location():
        try:
            location = JohnnyBox.get_location()
            return {'data': location}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500
        
    def create_location(data):
        location_name = data.get('location_name')
        try:
            JohnnyBox.create_location(location_name)
            return {"message": "Location create successfully"}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500
    
    def update_location(data):
        location_id = data.get('location_id')
        location_name = data.get('location_name')
        try:
            JohnnyBox.update_location(location_id, location_name)
            return {"message": "Location update successfully"}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500
    
    def delete_location(data):
        location_id = data.get('location_id')
        try:
            JohnnyBox.delete_location(location_id)
            return {"message": "Location delete successfully"}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500

class DocController:
    def get_doc_detail():
        try:
            documents = JohnnyDoc.get_document_detail()
            return {'data': documents}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500
        
    def get_all_document():
        try:
            documents = JohnnyDoc.get_all_document()
            return {'data': documents}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500
    
    def create_approve_pickup(data):
        approval_id = data.get('approval_id')
        requester_email = data.get('requester_email')
        approver_email = data.get('approver_email')
        approval_detail = data.get('approval_detail')
        try:
            DocInBox.create_approve_pickup(approval_id, requester_email, approver_email, approval_detail)
            return {"message": "Approve pickup create successfully"}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500

    def get_pickup_request(data):
        approval_id = data.get('approval_id')
        requester_email = data.get('requester_email')
        approver_email = data.get('approver_email')
        status = data.get('status')
        try:
            pickup_request = DocInBox.get_pickup_request(approval_id, requester_email, approver_email, status)
            return {'data': pickup_request}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500

    def update_request_status(data):
        print(f"=== DEBUG: update_request_status controller ===")
        print(f"Received data keys: {list(data.keys())}")
        print(f"Full data: {data}")
        
        approval_id = data.get('approval_id')
        approval_status = data.get('approval_status')
        approver_comment = data.get('approver_comment')
        approval_response = data.get('approval_response')
        
        print(f"Extracted values:")
        print(f"  approval_id: {approval_id}")
        print(f"  approval_status: {approval_status}")
        print(f"  approver_comment: {approver_comment}")
        print(f"  approval_response exists: {approval_response is not None}")
        print(f"  approval_response type: {type(approval_response)}")
        if approval_response:
            print(f"  approval_response length: {len(approval_response)}")
            print(f"  approval_response preview: {approval_response[:200]}...")
        
        if not approval_id or not approval_status:
            print("ERROR: Missing required fields")
            return {"message": "Missing required fields"}, 400
            
        if approval_status not in ['approved', 'rejected']:
            print("ERROR: Invalid approval status")
            return {"message": "Invalid approval status. Must be 'approved' or 'rejected'"}, 400
            
        try:
            print("Calling DocInBox.update_approval_status...")
            DocInBox.update_approval_status(approval_id, approval_status, approver_comment, approval_response)
            print("DocInBox.update_approval_status completed successfully")
            return {"message": "Approval request status updated successfully"}, 200
        except Exception as e:
            print(f"ERROR in update_request_status: {str(e)}")
            print(f"ERROR type: {type(e)}")
            return {"error": str(e)}, 500

    # def store_doc(data):
    #     box_id = data.get('box_id')
    #     # doc_year = data.get('document_year')
    #     #doc_type = data.get('Document_Type')
    #     documents = data.get('documents')
    #     user_email = data.get('user_email')

    #     if not box_id or not documents or not user_email:
    #         return {"message": "Missing required fields"}, 400

    #     try:
    #         #doctype_id = doc_type_to_number(doc_type)

    #         box_data = JohnnyBox.get_box_by_id(box_id)
    #         if not box_data:
    #             return {"message": "Box not found"}, 404
    #         if box_data.box_close == 1:
    #             return {"message": "This box is closed, please open it before proceeding"}, 400

    #         created_docs = []
    #         for doc in documents:
    #             doc_year = doc[:4]

    #             # 3 ตัวถัดไป
    #             doc_type_raw = doc[4:7]

    #             # เช็คตัวที่ 3 ของ doc_type_raw
    #             if doc_type_raw[2] == "0":
    #                 doctype_id = doc_type_raw[:2]
    #             else:
    #                 doctype_id = doc_type_raw

    #             if  str(box_data.boxtype_id) != doctype_id:
    #                 return {"message": "Document type does not match box type"}, 400
                
    #             if box_data.box_year != doc_year:
    #                 return {"message": "Document year does not match box year"}, 400
                
    #             # doc_number = doc.get('ManageDocument')
    #             # doc_id = f"{doc_year}{doc}"
    #             created_doc = JohnnyDoc.create_doc(doc_year, doctype_id, doc[4:13], user_email)
    #             created_docs.append(created_doc)

    #             # Create a DocInBox entry
    #             uuid_id = uuid4().hex
    #             DocInBox.create_docInBox(uuid_id, doc, box_id)

    #         # Close the box after storing documents
    #         # JohnnyBox.update_box_status("CLOSE", user_email, box_id)

    #         return {"message": "Documents stored successfully", "stored_docs": created_docs, "box_id": box_id}, 201

    #     except Exception as e:
    #         return {"message": f"An error occurred: {str(e)}"}, 500

    def store_doc(data):
        box_id = data.get('box_id')
        documents = data.get('documents')
        user_email = data.get('user_email')

        if not box_id or not documents or not user_email:
            return {"message": "Missing required fields"}, 400

        try:
            box_data = JohnnyBox.get_box_by_id(box_id)
            if not box_data:
                return {"message": "Box not found"}, 404

            results = []  # เก็บผลลัพธ์ของเอกสารแต่ละตัว

            for doc in documents:
                try:
                    doc_year = doc[:4]
                    doc_type_raw = doc[4:7]

                    if doc_type_raw[2] == "0":
                        doctype_id = doc_type_raw[:2]
                    else:
                        doctype_id = doc_type_raw

                    errors = []

                    # ตรวจสอบ year
                    if str(box_data.box_year) != doc_year:
                        errors.append("ปีของเอกสารไม่ตรงกับปีของกล่อง")

                    # ตรวจสอบ type
                    if str(box_data.boxtype_id) != doctype_id:
                        errors.append("ประเภทของเอกสารไม่ตรงกับประเภทของกล่อง")

                    # ตรวจสอบว่าเอกสารนี้อยู่ในกล่องอื่นหรือไม่
                    existing_doc = DocInBox.get_doc_by_id(doc)
                    if existing_doc and existing_doc.get('box_id') != box_id:
                        errors.append(f"เอกสารเลขนี้ {doc} อยู่ในกล่อง {existing_doc.get('box_id')} แล้ว")

                    if errors:
                        results.append({
                            "doc": doc,
                            "status": "error",
                            "reasons": errors
                        })
                        continue

                    # ผ่าน validation → บันทึก
                    created_doc = JohnnyDoc.create_doc(doc_year, doctype_id, doc[4:13], user_email)
                    uuid_id = uuid4().hex
                    DocInBox.create_docInBox(uuid_id, doc, box_id)

                    results.append({
                        "doc": doc,
                        "status": "success",
                        # "created_doc": created_doc
                    })

                except Exception as e:
                    results.append({
                        "doc": doc,
                        "status": "error",
                        "reasons": [str(e)]
                    })


            return {
                "message": "Documents processed",
                "results": results,
                "box_id": box_id
            }, 200

        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

    def remove_docInBox(data):
        box_id = data.get('box_id')
        documents = data.get('documents')
        user_email = data.get('user_email')

        if not box_id or not documents or not user_email:
            return {"message": "Missing required fields"}, 400

        try:
            box_data = JohnnyBox.get_box_by_id(box_id)
            if not box_data:
                return {"message": "Box not found"}, 404

            results = []  # เก็บผลลัพธ์ของเอกสารแต่ละตัว

            for doc in documents:
                try:
                    doc_year = doc[:4]
                    doc_type_raw = doc[4:7]

                    if doc_type_raw[2] == "0":
                        doctype_id = doc_type_raw[:2]
                    else:
                        doctype_id = doc_type_raw

                    errors = []

                    # ตรวจสอบ year
                    if str(box_data.box_year) != doc_year:
                        errors.append("ปีของเอกสารไม่ตรงกับปีของกล่อง")

                    # ตรวจสอบ type
                    if str(box_data.boxtype_id) != doctype_id:
                        errors.append("ประเภทของเอกสารไม่ตรงกับประเภทของกล่อง")

                    if errors:
                        results.append({
                            "doc": doc,
                            "status": "error",
                            "reasons": errors
                        })
                        continue

                    # ผ่าน validation → บันทึก
                    removed_docs = DocInBox.remove_docInBox(doc, box_id, user_email)

                    results.append({
                        "doc": doc,
                        "status": "success",
                        # "removed_doc": removed_docs
                    })

                except Exception as e:
                    results.append({
                        "doc": doc,
                        "status": "error",
                        "reasons": [str(e)]
                    })
            return {
                "message": "Documents processed",
                "results": results,
                "box_id": box_id
            }, 200

        except Exception as e:
            return {"message": f"An error occurred: {str(e)}"}, 500

class SearchController:

    # def search(data):
    #     id = data.get('id')
    #     year = data.get('year')
    #     type = data.get('type')
    #     location = data.get('location')
    #     category = data.get('category')
    #     try:
    #         if category == "box":
    #             res = Search.search_boxes(id, year, type, location)
    #         elif category == "document":
    #             res = Search.search_documents(id, year, type, location)
    #         else:
    #             return {"error": "Invalid category. Must be 'box' or 'document'."}, 400

    #         return {'data': res}, 200
    #     except Exception as e:
    #         return {"error": str(e)}, 500
    def search(data):
        ids = data.get('id')  # อาจเป็น string หรือ list
        year = data.get('year')
        type = data.get('type')
        location = data.get('location')
        category = data.get('category')
        try:
            if category == "box":
                res = Search.search_boxes(ids, year, type, location)
            elif category == "document":
                res = Search.search_documents(ids, year, type, location)
            else:
                return {"error": "Invalid category. Must be 'box' or 'document'."}, 400

            return {'data': res}, 200
        except Exception as e:
            return {"error": str(e)}, 500

class UserController:
        
    def get_user(data):
        user_email = data.get('user_email')
        try:
            user = UserManagement.get_user(user_email)
            return {'data': user}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500

    def get_approver():
        try:
            user = UserManagement.get_approver()
            return {'data': user}, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500

    def get_approver_by_email(data):
        user_email = data.get('user_email')
        try:
            is_approver = UserManagement.get_approver_by_email(user_email)
            return is_approver, 200  # Return as a dictionary with status code
        except Exception as e:
            return {"error": str(e)}, 500

    
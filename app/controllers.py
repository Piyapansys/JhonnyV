from datetime import datetime
from uuid import uuid4
from app.models import DocfinderBox,DocfinderDoc,DocInBox
from app.__init__ import db

# สร้าง dictionary สำหรับ mapping box_type กับตัวเลข
TYPE_MAPPING = {
    "KY": 212,
    "KZ": 211,
    "SV": 701,
    "DP": 311,
    "RP": 65,
    "RR": 69,
    "DC": 302,
    "TD": 713
}

def map_type_to_number(type):
    if type in TYPE_MAPPING:
        return TYPE_MAPPING[type]
    else:
        raise ValueError(f"Invalid type: {type}")

def create_box(data):
    # ดึงข้อมูลจาก JSON
    box_type = data.get('box_type')
    box_year = data.get('box_year')
    create_amount = int(data.get('create_amount', 1))  # จำนวนกล่องที่ต้องสร้าง
    user_email = data.get('user_email')

    # ตรวจสอบข้อมูลที่จำเป็น
    if not box_type or not box_year or not user_email:
        return {"message": "Missing required fields"}, 400
    
    # แปลง box_type เป็นหมายเลข
    try:
        box_type = map_type_to_number(data['box_type'])
    except ValueError as e:
        return {"message": str(e)}, 400  # ส่งข้อความ error กลับถ้า box_type ไม่ถูกต้อง
    
    created_boxes = []
    for i in range(create_amount):
        # หา box_id และ box_number ถัดไป
        box_id, next_box_number = DocfinderBox.get_next_box_id(box_year, box_type)

        # สร้างอินสแตนซ์ของ `DocfinderBox` โดยเรียกใช้ `create_box`
        new_box = DocfinderBox.create_box(box_year, box_type, user_email)
        created_boxes.append(box_id)

    # บันทึกลงฐานข้อมูล
    db.session.commit()

    # ส่งกลับรายการกล่องที่สร้าง
    return {
        "message": "Boxes created successfully",
        "created_boxes": created_boxes
    }

def update_box_status(data):
    # ดึงข้อมูลจาก JSON
    boxs = data.get('Box')  # จำนวนกล่องที่ต้องสร้าง
    box_action = data.get('BoxAction')
    user_email = data.get('UserEmail')
    
    manage_Boxs = [i.get('ManageBoxNumber') for i in boxs]

    # ตรวจสอบข้อมูลที่จำเป็น
    if not manage_Boxs or not box_action or not user_email:
        return {"message": "Missing required fields"}, 400

    for box_number in manage_Boxs:
        box_data = DocfinderBox.get_box_by_id(box_number)
        if not box_data:
            return {"message": "Box not found"}, 404
        
        if box_action == "OPEN":
            box_data.box_close = False
        elif box_action == "CLOSE":
            box_data.box_close = True

        box_data.update_at = datetime.now()
        box_data.update_by = user_email

    db.session.commit()  # commit หลังจากเพิ่มข้อมูลทั้งหมด

    # ส่งกลับรายการกล่องที่สร้าง
    return {
        "message": "Box status changed successfully",
        "changed_boxs": manage_Boxs
    }

def store_doc(data):
    # ดึงข้อมูลจาก JSON
    box_id = data.get('BoxID')
    doc_year = data.get('Document_Year')
    doc_type = data.get('Document_Type')
    documents = data.get('Documents')  # จำนวนกล่องที่ต้องสร้าง
    user_email = data.get('UserEmail')
    
    manage_documents = [i.get('ManageDocument') for i in documents]

    # ตรวจสอบข้อมูลที่จำเป็น
    if not doc_type or not doc_year or not user_email:
        return {"message": "Missing required fields"}, 400

    if len(doc_year) != 4 or not doc_year.isdigit():
        return {"message": "DocYear must be a 4-digit number"}, 400
    
    # แปลง box_type เป็นหมายเลข
    doctype_id = map_type_to_number(doc_type)
    if doctype_id is None:
        return {"message": "Invalid document type"}, 400

    # ดึงข้อมูล Box ที่มี box_id ตรงกันจากฐานข้อมูล
    box_data = DocfinderBox.get_box_by_id(box_id)
    if not box_data:
        return {"message": "Box not found"}, 404

    # ตรวจสอบว่า doc_type และ doc_year ตรงกับข้อมูล box_type_id และ box_year หรือไม่
    if box_data.boxtype_id != doctype_id:
        return {"message": "Document type does not match with box type"}, 400
    if box_data.box_year != doc_year:
        return {"message": "Document year does not match with box year"}, 400
    if box_data.box_close == 1:
        return {"message": "กล่องนี้ถูกปิดไปแล้วจ้าาา รบกวนทำการเปิดกล่องแล้วทำรายการอีกครั้ง"}, 400
    
    created_docs = []
    doc_in_box_objects = []  # สร้างรายการเพื่อเก็บ DocInBox ทั้งหมด

    for doc_number in manage_documents:
        doc_id = f"{doc_year}{doc_number}"
        # สร้าง `DocfinderDoc` โดยใช้ method ของ model
        DocfinderDoc.create_doc(doc_year, doctype_id, doc_number, user_email,box_id)
        created_docs.append(doc_id)

        # สร้าง `DocInBox` object เพื่อเพิ่มลงฐานข้อมูล
        uuid_id = uuid4().hex
        new_doc_in_box = DocInBox.create_docInBox(id=uuid_id, doc_id=doc_id, box_id=box_id)
        doc_in_box_objects.append(new_doc_in_box)  # เก็บข้อมูลเพื่อ commit ทีเดียว

    # เพิ่มข้อมูลทั้งหมดลงฐานข้อมูลทีเดียว
    db.session.add_all(doc_in_box_objects)
    box_data.box_close = True  # สมมติว่า box_close เป็นคอลัมน์ในตาราง DocfinderBox
    box_data.update_at = datetime.now()
    box_data.update_by = user_email
    db.session.commit()  # commit หลังจากเพิ่มข้อมูลทั้งหมด

    # ส่งกลับรายการกล่องที่สร้าง
    return {
        "message": "Docs stored successfully",
        "stored_docs": created_docs,
        "at_box": box_id
    }

def remove_doc(data):
    # ดึงข้อมูลจาก JSON
    box_id = data.get('BoxID')
    doc_year = data.get('Document_Year')
    doc_type = data.get('Document_Type')
    documents = data.get('Documents')  # จำนวนกล่องที่ต้องสร้าง
    user_email = data.get('UserEmail')
    
    manage_documents = [i.get('ManageDocument') for i in documents]

    # ตรวจสอบข้อมูลที่จำเป็น
    if not doc_type or not doc_year or not user_email:
        return {"message": "Missing required fields"}, 400

    if len(doc_year) != 4 or not doc_year.isdigit():
        return {"message": "DocYear must be a 4-digit number"}, 400

    doctype_id = map_type_to_number(doc_type)
    if doctype_id is None:
        return {"message": "Invalid document type"}, 400
    
    # ดึงข้อมูล Box ที่มี box_id ตรงกันจากฐานข้อมูล
    box_data = DocfinderBox.get_box_by_id(box_id)
    if not box_data:
        return {"message": "Box not found"}, 404

    # ตรวจสอบว่า doc_type และ doc_year ตรงกับข้อมูล box_type_id และ box_year หรือไม่
    if box_data.boxtype_id != doctype_id:
        return {"message": "Document type does not match with box type"}, 400
    if box_data.box_year != doc_year:
        return {"message": "Document year does not match with box year"}, 400
    if box_data.box_close == 1:
        return {"message": "กล่องนี้ถูกปิดไปแล้วจ้าาา รบกวนทำการเปิดกล่องแล้วทำรายการอีกครั้ง"}, 400

    for doc_number in manage_documents:
        doc_id = f"{doc_year}{doc_number}"
        # สร้าง `DocInBox` object เพื่อเพิ่มลงฐานข้อมูล
        remove_record = DocInBox.remove_docInBox(doc_id=doc_id, box_id=box_id)
        print(remove_record)
        if not remove_record:
            return {"message": "No matching record found to delete","OnDoc": doc_number,"OnBox": box_id }, 404
        
        doc_data = DocfinderDoc.get_doc_by_id(doc_id)
        if not doc_data:
            return {"message": "Doc not found"}, 404
        
        doc_data.remove_at = datetime.now()
        doc_data.remove_by = user_email

    box_data.box_close = True  # สมมติว่า box_close เป็นคอลัมน์ในตาราง DocfinderBox
    box_data.update_at = datetime.now()
    box_data.update_by = user_email
    db.session.commit()
    # ส่งกลับรายการกล่องที่สร้าง
    return {
        "message": "Docs removed successfully",
        "at_docs": manage_documents
    }
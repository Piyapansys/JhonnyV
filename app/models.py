from datetime import datetime
from app.__init__ import db
from sqlalchemy import Column
from uuid import uuid4

class DocfinderBox(db.Model):
    __tablename__ = 'docfinder_box'  # ชื่อตารางในฐานข้อมูล
    box_id = Column(db.String(15), primary_key=True)  # Primary Key
    box_year = Column(db.String(4), nullable=False)
    boxtype_id = Column(db.Integer, nullable=False)  # Foreign Key
    box_number = Column(db.Integer, nullable=False)
    box_close = Column(db.Boolean, default=False)
    update_at = Column(db.DateTime, nullable=True)
    update_by = Column(db.String(50), nullable=True)
    created_at = Column(db.DateTime, nullable=False, default=datetime.now)
    create_by = Column(db.String(50), nullable=False)

    @classmethod
    def get_box_by_id(cls, box_id):
        return db.session.query(cls).filter(cls.box_id == box_id).first()
    # เมธอดคลาสสำหรับหาหมายเลขกล่องถัดไปและสร้าง ID กล่องใหม่
    @classmethod
    def get_next_box_id(cls, box_year, box_type):
        # ค้นหา box_number ล่าสุดที่ตรงกับปีและประเภท
        last_box = cls.query.filter_by(box_year=box_year, boxtype_id=box_type).order_by(cls.box_number.desc()).first()
        # หา box_number ถัดไป
        if last_box:
            next_box_number = last_box.box_number + 1
        else:
            next_box_number = 1
        # สร้าง box_id ใหม่
        if len(box_year) == 4 and box_year.isdigit():
            box_year = box_year[2:]  # ตัดเอาแค่ 2 ตัวหลัง
        else:
            return {"message": "Year must be a 4-digit number"}, 400
        
        box_id = f"0490AC{box_year}J{box_type}{str(next_box_number).zfill(3)}"
        return box_id, next_box_number

    # เมธอดสำหรับการสร้างกล่องใหม่
    @classmethod
    def create_box(cls, box_year, box_type, create_by):
        # สร้าง box_id ใหม่และหมายเลขกล่องถัดไป
        box_id, next_box_number = cls.get_next_box_id(box_year, box_type)
        # สร้าง object ของ DocfinderBox
        new_box = cls(
            box_id=box_id,
            boxtype_id=box_type,
            box_year=box_year,
            box_number=next_box_number,  # ใช้หมายเลขกล่องที่ได้จากการคำนวณ
            create_by=create_by,
            created_at=datetime.now()
        )
        # เพิ่มข้อมูลลงใน session แต่ไม่ทำการ commit()
        db.session.add(new_box)
        return new_box

class DocfinderDoc(db.Model):
    __tablename__ = 'docfinder_doc'  # ชื่อตารางในฐานข้อมูล
    doc_id = Column(db.String(15), primary_key=True)  # Primary Key
    doc_year = Column(db.String(4), nullable=False)
    doctype_id = Column(db.Integer, nullable=False)  # Foreign Key
    doc_number = Column(db.Integer, nullable=False)
    remove_at = Column(db.DateTime, nullable=True)
    remove_by = Column(db.String(50), nullable=True)
    store_at = Column(db.DateTime, nullable=False, default=datetime.now)
    store_by = Column(db.String(50), nullable=False)
    #เมธอดสำหรับการสร้างเอกสารใหม่

    @classmethod
    def create_doc(cls, doc_year, doctype_id, doc_number, store_by,box_id):
        doc_id = f"{doc_year}{doc_number}"
        # สร้าง object ของ DocfinderBox
        update_doc = DocfinderDoc.query.filter_by(doc_id=doc_id).first()
        update_doc_in_box = DocInBox.query.filter_by(doc_id=doc_id, box_id=box_id).first()
        
        if update_doc != None and update_doc_in_box is None:
            doc_data = DocfinderDoc.get_doc_by_id(doc_id)  
            doc_data.store_at = datetime.now()
            doc_data.store_by = store_by
            db.session.commit()
        elif update_doc is None and update_doc_in_box is None :
            new_doc = cls(
                doc_id=doc_id,
                doctype_id=doctype_id,
                doc_year=doc_year,
                doc_number=doc_number,  # ใช้หมายเลขกล่องที่ได้จากการคำนวณ
                store_by=store_by,
                store_at=datetime.now()
            )
            db.session.add(new_doc)
            db.session.commit()
            return new_doc
        
    
    @classmethod
    def get_doc_by_id(cls, doc_id):
        return db.session.query(cls).filter(cls.doc_id == doc_id).first()
    
    
class DocInBox(db.Model):
    __tablename__ = 'docfinder_docInBox'  # ชื่อตารางในฐานข้อมูล
    id = Column(db.String, primary_key=True)  # Primary Key
    doc_id = Column(db.String, nullable=False) # Foreign Key
    box_id = Column(db.String, nullable=False)  # Foreign Key

    @classmethod
    def create_docInBox(cls,id, doc_id,box_id):
        # สร้าง object ของ DocfinderBox
        new_docInBox = cls(
            id = id,
            doc_id = doc_id,
            box_id = box_id
        )
        # เพิ่มข้อมูลลงฐานข้อมูล
        db.session.add(new_docInBox)
        db.session.commit()
        return new_docInBox
    
    @classmethod
    def remove_docInBox(cls, doc_id,box_id):
        remove_doc_in_box = DocInBox.query.filter_by(doc_id=doc_id, box_id=box_id).first()
        # เพิ่มข้อมูลลงฐานข้อมูล
        print(remove_doc_in_box)
        if remove_doc_in_box is None:
            return remove_doc_in_box
        else:
            db.session.delete(remove_doc_in_box)
            db.session.commit()
        
    
    
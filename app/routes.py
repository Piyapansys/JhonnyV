from flask import request
from flask_restx import Namespace, Resource, fields
from app.controllers import create_box ,store_doc,remove_doc,update_box_status

box_api = Namespace('api/boxes', description='Box operations')

create_box_model = box_api.model('BoxCreateModel', {
    'box_type': fields.String(required=True, description='เลือกประเภทของกล่องที่จะจัดเก็บ'),
    'box_year': fields.String(required=True, description='เลือกปีของเอกสารที่จะจัดเก็บ'),
    'create_amount': fields.Integer(required=True,default=1 , description='จำนวนของกล่องที่จะสร้าง'),
    'user_email': fields.String(required=True, description='อีเมลของผู้ใช้งาน')
})

box_model = box_api.model('Box', {
    'BoxID': fields.String(required=True, description='Unable to use ID'),
    'ManageBoxNumber': fields.String(required=True, description='Box ID')
})
box_status = box_api.model('BoxStatusModel', {
    'Box': fields.List(fields.Nested(box_model), description='เลขของกล่องที่ต้องการเปลี่ยนแปลงสถานะ'),
    'BoxAction': fields.String(required=True, description='สถานะที่จะเปลี่ยนแปลง'),
    'UserEmail': fields.String(required=True, description='อีเมลของผู้ใช้งาน')
})

@box_api.route('/create_box')
class BoxCreateResource(Resource):
    @box_api.expect(create_box_model)
    def post(self):
            """Create a new box"""
            data = request.json
            if 'box_year' not in data or 'box_type' not in data or 'user_email' not in data:
                return {"message": "box_year, box_type and user_email are required"}, 400
            return create_box(data)
    
@box_api.route('/update-status')
class BoxStatusResource(Resource):
    @box_api.expect(box_status)
    def post(self):
            """Box's Status Update"""
            data = request.json
            if 'Box' not in data or 'BoxAction' not in data or 'UserEmail' not in data:
                return {"message": "Box, BoxAction, UserEmail are required"}, 400
            return update_box_status(data)



doc_api = Namespace('api/docs', description='Doc operations')

# Model สำหรับ Document
document_model = doc_api.model('Document', {
    'ID': fields.String(required=True, description='Unable to use ID'),
    'ManageDocument': fields.String(required=True, description='Document ID')
})
# Model สำหรับ Box
doc_model = doc_api.model('DataModel', {
    'BoxID': fields.String(required=True, description='Box ID'),
    'Document_Year': fields.String(required=True, description='ปีของเอกสาร'),
    'Document_Type': fields.String(required=True, description='ประเภทของเอกสาร ครับ'),
    'Documents': fields.List(fields.Nested(document_model), description='เอกสารในกล่อง'),
    'UserEmail': fields.String(required=True, description='อีเมลของผู้ใช้งาน')
})
@doc_api.route('/docInBox')
class DocMappingResource(Resource):
    @doc_api.expect(doc_model)
    def post(self):
            """Store Document Into the Box"""
            data = request.json
            if 'BoxID' not in data or 'Document_Year' not in data or 'Document_Type' not in data or 'Documents' not in data or 'UserEmail' not in data:
                return {"message": "BoxID, Document_Year, Document_Type, Documents and user_email are required"}, 400
            return store_doc(data)
    
@doc_api.route('/Remove-docInBox')
class DocRemoveResource(Resource):
    @doc_api.expect(doc_model)
    def delete(self):
            """Remove Document From the Box"""
            data = request.json
            if 'BoxID' not in data or 'Document_Year' not in data or 'Document_Type' not in data or 'Documents' not in data or 'UserEmail' not in data:
                return {"message": "BoxID, Document_Year, Document_Type, Documents and user_email are required"}, 400
            return remove_doc(data)
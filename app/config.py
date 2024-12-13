import os
from dotenv import load_dotenv

# โหลดค่าจากไฟล์ .env
load_dotenv()

# ดึงค่า environment variables ที่เก็บใน .env
server = os.getenv('DB_SERVER')
database = os.getenv('DB_DATABASE')
username = os.getenv('DB_USERNAME')
password = os.getenv('DB_PASSWORD')

class Config:
    # ฟอร์แมต string ด้วย f-string เพื่อใส่ตัวแปรเข้าไปใน URL
    SQLALCHEMY_DATABASE_URI = (
        f'mssql+pymssql://{username}:{password}@{server}/{database}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
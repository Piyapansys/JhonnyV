# class Config:
#     SQL_SERVER_CONNECTION = "Driver={ODBC Driver 17 for SQL Server};Server=1syscmpsy05;Database=WEBAC;UID=webac;PWD=webac"
#     SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={SQL_SERVER_CONNECTION}"  # เชื่อมต่อผ่าน ODBC
#     SQLALCHEMY_TRACK_MODIFICATIONS = False  # ปิดการติดตามการเปลี่ยนแปลงของ object เพื่อประหยัดทรัพยากร

class Config:
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc://webac:webac@1syscmpsy05/WEBAC?driver=ODBC+Driver+17+for+SQL+Server'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

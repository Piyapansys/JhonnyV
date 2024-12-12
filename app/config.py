class Config:
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc://administratorsys:DxIT$y$2023@siamyamato.database.windows.net:1433/thoth_datawarehouse?driver=ODBC+Driver+18+for+SQL+Server'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# class Config:
#     SQLALCHEMY_TRACK_MODIFICATIONS = False

#     # ODBC connection string for Azure SQL Database
#     DRIVER = "{ODBC Driver 18 for SQL Server}"
#     SERVER = "siamyamato.database.windows.net"
#     DATABASE = "thoth_datawarehouse"
#     UID = "administratorsys"
#     PWD = "DxIT$y$2023"
#     ENCRYPT = "yes"
#     TrustServerCertificate = "no"
#     TIMEOUT = 30
#     # SQLAlchemy Database URI
#     SQLALCHEMY_DATABASE_URI = (
#         f"mssql+pyodbc://{UID}:{PWD}@{SERVER}/{DATABASE}?driver={DRIVER}&Encrypt={ENCRYPT}&TrustServerCertificate={TrustServerCertificate}&timeout={TIMEOUT}"
#     )

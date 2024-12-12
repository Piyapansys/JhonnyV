class Config:
    SQLALCHEMY_DATABASE_URI = (
        'mssql+pyodbc://webac:webac@1syscmpsy05/WEBAC?driver=ODBC+Driver+17+for+SQL+Server'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

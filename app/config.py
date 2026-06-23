import os
from dotenv import load_dotenv
import configparser

# Load environment variables from .env file
load_dotenv()

class Config:
    # Database connection string
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Other configurations
    server = os.getenv('DB_SERVER')
    database = os.getenv('DB_DATABASE')
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pyodbc://{username}:{password}@{server}/{database}"
        "?driver=ODBC+Driver+18+for+SQL+Server"
        "&Encrypt=yes"
        "&TrustServerCertificate=yes"
        "&Connection Timeout=30"
    )
    SQL_SERVER_CONNECTION_STRING = (
        f"DRIVER={{ODBC Driver 18 for SQL Server}};"
        f"SERVER=tcp:{server},1433;"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        "Encrypt=yes;"
        "TrustServerCertificate=yes;"
        "Connection Timeout=30;"
        "ConnectRetryCount=3;"
        "ConnectRetryInterval=10;"
    )

    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        if os.path.exists(config_file):
            self.config.read(config_file)

    def get(self, section, option):
        return self.config.get(section, option)

    def getfloat(self, section, option):
        return self.config.getfloat(section, option)

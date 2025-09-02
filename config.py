import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration class"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    
    # SQL Server Configuration
    SQL_SERVER = os.environ.get('SQL_SERVER') or 'GOTARUO\\MSSQLSERVER01'
    SQL_DATABASE = os.environ.get('SQL_DATABASE') or 'WorkflowDB'
    SQL_USERNAME = os.environ.get('SQL_USERNAME') or 'sa'
    SQL_PASSWORD = os.environ.get('SQL_PASSWORD') or ''
    
    # File Upload Configuration
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Build SQL Server connection string
    @staticmethod
    def get_database_uri():
        if Config.SQL_PASSWORD:
            # SQL Server Authentication
            return f'mssql+pyodbc://{Config.SQL_USERNAME}:{Config.SQL_PASSWORD}@{Config.SQL_SERVER}/{Config.SQL_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server'
        else:
            # Windows Authentication (Trusted Connection)
            return f'mssql+pyodbc://{Config.SQL_SERVER}/{Config.SQL_DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

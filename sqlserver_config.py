import os

# SQL Server Configuration for Document Workflow System
# Values read from environment variables for public repositories

# SQL Server Instance Details
SQL_SERVER = os.getenv('SQL_SERVER', 'localhost')  # Your SQL Server instance name
SQL_DATABASE = os.getenv('SQL_DATABASE', 'WorkflowDB')  # Database name (will be created if it doesn't exist)

# Authentication Method
# Option 1: Windows Authentication (Recommended for development)
USE_WINDOWS_AUTH = os.getenv('USE_WINDOWS_AUTH', 'True').lower() == 'true'
SQL_USERNAME = os.getenv('SQL_USERNAME', '')  # Leave empty for Windows Authentication
SQL_PASSWORD = os.getenv('SQL_PASSWORD', '')  # Leave empty for Windows Authentication

# Option 2: SQL Server Authentication (Uncomment and configure if needed)
# USE_WINDOWS_AUTH = False
# SQL_USERNAME = 'sa'  # SQL Server username
# SQL_PASSWORD = 'your_password_here'  # SQL Server password

# Connection Settings
SQL_TIMEOUT = 30  # Connection timeout in seconds
SQL_POOL_SIZE = 10  # Connection pool size
SQL_MAX_OVERFLOW = 20  # Maximum overflow connections

# ODBC Driver
# Make sure you have the appropriate ODBC driver installed
# For SQL Server 2019+: ODBC Driver 17 for SQL Server
# For SQL Server 2016: ODBC Driver 13 for SQL Server
ODBC_DRIVER = os.getenv('ODBC_DRIVER', 'ODBC Driver 17 for SQL Server')

# Alternative drivers (uncomment if needed):
# ODBC_DRIVER = 'ODBC Driver 13 for SQL Server'  # For SQL Server 2016
# ODBC_DRIVER = 'SQL Server'  # Legacy driver (not recommended)

def get_connection_string():
    """Generate the SQL Server connection string based on configuration"""
    if USE_WINDOWS_AUTH:
        # Windows Authentication (Trusted Connection) - Fixed format for pyodbc
        return f"DRIVER={{{ODBC_DRIVER}}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;Timeout={SQL_TIMEOUT};"
    else:
        # SQL Server Authentication - Fixed format for pyodbc
        return f"DRIVER={{{ODBC_DRIVER}}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};UID={SQL_USERNAME};PWD={SQL_PASSWORD};Timeout={SQL_TIMEOUT};"

def get_connection_string_with_pool():
    """Generate connection string with connection pooling"""
    base_string = get_connection_string()
    pool_settings = f"Pooling=yes;MaxPoolSize={SQL_POOL_SIZE};"
    return base_string + pool_settings

def get_flask_sqlalchemy_uri():
    """Generate Flask-SQLAlchemy compatible connection string"""
    if USE_WINDOWS_AUTH:
        # Windows Authentication for Flask-SQLAlchemy
        return f"mssql+pyodbc:///?odbc_connect={get_connection_string()}"
    else:
        # SQL Server Authentication for Flask-SQLAlchemy
        return f"mssql+pyodbc://{SQL_USERNAME}:{SQL_PASSWORD}@/?odbc_connect={get_connection_string()}"

# Print current configuration for verification
if __name__ == '__main__':
    print("SQL Server Configuration:")
    print(f"Server: {SQL_SERVER}")
    print(f"Database: {SQL_DATABASE}")
    print(f"Authentication: {'Windows Authentication' if USE_WINDOWS_AUTH else 'SQL Server Authentication'}")
    if not USE_WINDOWS_AUTH:
        print(f"Username: {SQL_USERNAME}")
    print(f"ODBC Driver: {ODBC_DRIVER}")
    print(f"Connection String: {get_connection_string()}")
    print(f"Flask-SQLAlchemy URI: {get_flask_sqlalchemy_uri()}")

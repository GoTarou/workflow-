#!/usr/bin/env python3
"""
SQL Server Connection Test Script
This script tests the connection to your SQL Server instance before running the main application.
"""

import pyodbc
import sys
from sqlserver_config import get_connection_string, SQL_SERVER, SQL_DATABASE, USE_WINDOWS_AUTH

def test_odbc_drivers():
    """Test available ODBC drivers"""
    print("🔍 Checking available ODBC drivers...")
    try:
        drivers = pyodbc.drivers()
        if drivers:
            print("✅ Available ODBC drivers:")
            for driver in drivers:
                print(f"   - {driver}")
        else:
            print("❌ No ODBC drivers found!")
            return False
        return True
    except Exception as e:
        print(f"❌ Error checking ODBC drivers: {e}")
        return False

def test_connection():
    """Test SQL Server connection"""
    print(f"\n🔌 Testing connection to SQL Server: {SQL_SERVER}")
    print(f"📊 Database: {SQL_DATABASE}")
    print(f"🔐 Authentication: {'Windows Authentication' if USE_WINDOWS_AUTH else 'SQL Server Authentication'}")
    
    try:
        # Test connection using the corrected connection string
        conn_str = get_connection_string()
        print(f"\n🔗 Connection string: {conn_str}")
        
        print("\n🔄 Attempting to connect...")
        conn = pyodbc.connect(conn_str)
        
        print("✅ Connection successful!")
        
        # Test basic operations
        cursor = conn.cursor()
        
        # Test server info
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        # Fix the backslash issue in the version string
        version_line = version.split('\n')[0] if '\n' in version else version
        print(f"📋 SQL Server Version: {version_line}")
        
        # Test database existence
        cursor.execute("SELECT name FROM sys.databases WHERE name = ?", SQL_DATABASE)
        db_exists = cursor.fetchone()
        
        if db_exists:
            print(f"✅ Database '{SQL_DATABASE}' exists")
            
            # Test table access
            cursor.execute(f"USE {SQL_DATABASE}")
            cursor.execute("SELECT COUNT(*) FROM sys.tables")
            table_count = cursor.fetchone()[0]
            print(f"📊 Tables in database: {table_count}")
            
        else:
            print(f"⚠️  Database '{SQL_DATABASE}' does not exist")
            print("💡 Run the setup_sqlserver.sql script to create it")
        
        cursor.close()
        conn.close()
        return True
        
    except pyodbc.Error as e:
        print(f"❌ SQL Server connection failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Verify SQL Server is running")
        print("   2. Check instance name spelling")
        print("   3. Ensure ODBC driver is installed")
        print("   4. Verify Windows Authentication is enabled")
        return False
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database_creation():
    """Test if we can create the database"""
    print(f"\n🏗️  Testing database creation permissions...")
    
    try:
        # Connect to master database using corrected format
        if USE_WINDOWS_AUTH:
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE=master;Trusted_Connection=yes;"
        else:
            from sqlserver_config import SQL_USERNAME, SQL_PASSWORD
            conn_str = f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE=master;UID={SQL_USERNAME};PWD={SQL_PASSWORD};"
        
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()
        
        # Test CREATE DATABASE permission
        cursor.execute("SELECT HAS_PERMS_BY_NAME(NULL, NULL, 'CREATE ANY DATABASE')")
        can_create = cursor.fetchone()[0]
        
        if can_create:
            print("✅ You have permission to create databases")
        else:
            print("⚠️  You don't have permission to create databases")
            print("💡 Contact your SQL Server administrator")
        
        cursor.close()
        conn.close()
        return can_create
        
    except Exception as e:
        print(f"❌ Error testing permissions: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🚀 SQL Server Connection Test")
    print("=" * 60)
    
    # Test 1: ODBC Drivers
    if not test_odbc_drivers():
        print("\n❌ ODBC driver test failed. Please install the appropriate driver.")
        sys.exit(1)
    
    # Test 2: Connection
    if not test_connection():
        print("\n❌ Connection test failed. Please check your configuration.")
        sys.exit(1)
    
    # Test 3: Database creation permissions
    test_database_creation()
    
    print("\n" + "=" * 60)
    print("✅ All tests completed successfully!")
    print("🎉 You're ready to run the Document Workflow System!")
    print("=" * 60)
    
    print("\n📋 Next steps:")
    print("   1. Run setup_sqlserver.sql in SSMS to create the database")
    print("   2. Run 'flask init-db' to initialize the application")
    print("   3. Run 'python run.py' to start the application")

if __name__ == '__main__':
    main()

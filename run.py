#!/usr/bin/env python3
"""
Document Workflow System - Startup Script
This script initializes the database and starts the Flask application.
"""

import os
import sys
from app import app, db

def init_database():
    """Initialize the database and create sample data."""
    try:
        with app.app_context():
            # Create all tables
            db.create_all()
            print("✅ Database tables created successfully!")
            
            # Check if we need to create sample data
            from app import User
            if not User.query.first():
                print("📝 Creating sample users...")
                
                # Import the init_db command and run it
                from app import init_db
                init_db()
                print("✅ Sample data created successfully!")
            else:
                print("ℹ️  Database already contains data, skipping sample data creation.")
                
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

def main():
    """Main function to start the application."""
    print("🚀 Starting Document Workflow System...")
    
    # Initialize database
    init_database()
    
    # Start the application
    print("🌐 Starting Flask application...")
    print("📍 Application will be available at: http://localhost:5000")
    print("🔑 Demo accounts:")
    print("   - Admin: admin / admin123")
    print("   - Approver: approver1 / approver123")
    print("   - User: user1 / user123")
    print("\n🛑 Press Ctrl+C to stop the application")
    print("-" * 50)
    
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()

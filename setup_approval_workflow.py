#!/usr/bin/env python3
"""
Setup script for the Approval Workflow System
This script will create the necessary database tables and populate them with sample data.
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, DepartmentApprover
from werkzeug.security import generate_password_hash
from datetime import datetime

def setup_database():
    """Create all database tables"""
    print("🗄️  Creating database tables...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully!")
        
        # Create sample users (this function is idempotent)
        create_sample_users()
        
        # Create department approvers (this function is idempotent)
        create_department_approvers()
        
        print("🎉 Approval workflow system setup completed!")

def create_sample_users():
    """Create sample users for testing"""
    print("👥 Creating sample users...")
    
    users = [
        {
            'username': 'admin',
            'email': 'admin@company.com',
            'password': 'admin123',
            'role': 'admin',
            'department': 'Management'
        },
        {
            'username': 'hr_manager',
            'email': 'hr@company.com',
            'password': 'hr123',
            'role': 'approver',
            'department': 'HR'
        },
        {
            'username': 'sales_director',
            'email': 'sales@company.com',
            'password': 'sales123',
            'role': 'approver',
            'department': 'Sales'
        },
        {
            'username': 'facilities_manager',
            'email': 'facilities@company.com',
            'password': 'facilities123',
            'role': 'approver',
            'department': 'Facilities'
        },
        {
            'username': 'it_manager',
            'email': 'it@company.com',
            'password': 'it123',
            'role': 'approver',
            'department': 'IT'
        },
        {
            'username': 'employee1',
            'email': 'employee1@company.com',
            'password': 'emp123',
            'role': 'user',
            'department': 'Sales'
        },
        {
            'username': 'employee2',
            'email': 'employee2@company.com',
            'password': 'emp123',
            'role': 'user',
            'department': 'HR'
        }
    ]
    
    for user_data in users:
        # Check if user already exists
        existing_user = User.query.filter_by(username=user_data['username']).first()
        if existing_user:
            print(f"   ⚠️  User {user_data['username']} already exists, skipping...")
            continue
        
        # Create new user
        user = User(
            username=user_data['username'],
            email=user_data['email'],
            password_hash=generate_password_hash(user_data['password']),
            role=user_data['role'],
            department=user_data['department'],
            created_at=datetime.utcnow()
        )
        
        db.session.add(user)
        print(f"   ✅ Created user: {user_data['username']} ({user_data['role']})")
    
    db.session.commit()
    print("✅ Sample users created successfully!")

def create_department_approvers():
    """Create department approver assignments"""
    print("👨‍💼 Creating department approvers...")
    
    # Get the approver users
    hr_approver = User.query.filter_by(username='hr_manager').first()
    sales_approver = User.query.filter_by(username='sales_director').first()
    facilities_approver = User.query.filter_by(username='facilities_manager').first()
    it_approver = User.query.filter_by(username='it_manager').first()
    
    # Create department approver assignments
    departments = [
        ('HR', hr_approver.id),
        ('Sales', sales_approver.id),
        ('Facilities', facilities_approver.id),
        ('IT', it_approver.id),
        ('Other', hr_approver.id)  # HR manager handles general requests
    ]
    
    for dept_name, approver_id in departments:
        # Check if this department approver already exists
        existing = DepartmentApprover.query.filter_by(department=dept_name).first()
        if not existing:
            dept_approver = DepartmentApprover(
                department=dept_name,
                approver_id=approver_id,
                is_active=True
            )
            db.session.add(dept_approver)
            print(f"   ✅ Created approver for {dept_name}")
        else:
            print(f"   ⚠️  Approver for {dept_name} already exists, skipping...")
    
    db.session.commit()
    print("✅ Department approvers created successfully!")

def show_login_credentials():
    """Display login credentials for testing"""
    print("\n🔑 Login Credentials for Testing:")
    print("=" * 50)
    print("Admin User:")
    print("   Username: admin")
    print("   Password: admin123")
    print("   Role: Admin (can manage everything)")
    print()
    print("Department Approvers:")
    print("   HR Manager: hr_manager / hr123")
    print("   Sales Director: sales_director / sales123")
    print("   Facilities Manager: facilities_manager / facilities123")
    print("   IT Manager: it_manager / it123")
    print()
    print("Regular Employees:")
    print("   Employee 1: employee1 / emp123")
    print("   Employee 2: employee2 / emp123")
    print()
    print("💡 Test the workflow:")
    print("   1. Login as an employee and submit a request")
    print("   2. Login as the appropriate department approver to approve/reject")
    print("   3. Login as admin for final approval")
    print("   4. Use the 'Manage Approvers' page to assign different approvers")

if __name__ == "__main__":
    try:
        print("🚀 Setting up Approval Workflow System...")
        print("=" * 50)
        
        setup_database()
        show_login_credentials()
        
        print("\n🎯 Next steps:")
        print("   1. Run your Flask application: python app.py")
        print("   2. Login with the credentials above")
        print("   3. Test the approval workflow system")
        
    except Exception as e:
        print(f"❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python3
"""
Test script for the Approval Workflow System
Tests the complete workflow from request submission to approval
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db, User, Request, DepartmentApprover, RequestApproval
from router_ai_config import router_ai

def test_approval_workflow():
    """Test the complete approval workflow"""
    print("🧪 Testing Approval Workflow System")
    print("=" * 50)
    
    with app.app_context():
        # Test 1: Check if users exist
        print("\n1️⃣ Testing User Setup...")
        users = User.query.all()
        print(f"   ✅ Found {len(users)} users")
        
        admin_users = User.query.filter_by(role='admin').all()
        approver_users = User.query.filter_by(role='approver').all()
        regular_users = User.query.filter_by(role='user').all()
        
        print(f"   👑 Admin users: {len(admin_users)}")
        print(f"   👨‍💼 Approver users: {len(approver_users)}")
        print(f"   👷 Regular users: {len(regular_users)}")
        
        # Test 2: Check department approvers
        print("\n2️⃣ Testing Department Approvers...")
        approvers = DepartmentApprover.query.filter_by(is_active=True).all()
        print(f"   ✅ Found {len(approvers)} active department approvers")
        
        for approver in approvers:
            user = User.query.get(approver.approver_id)
            print(f"   📋 {approver.department}: {user.username}")
        
        # Test 3: Test Router AI message routing
        print("\n3️⃣ Testing Router AI Message Routing...")
        test_messages = [
            "Hi, I need to request vacation time for next week. Can you help me with the process?",
            "Our customer ABC Corp wants to place a large order. I need to discuss pricing options.",
            "The air conditioning in the office isn't working properly. Can someone check it?",
            "I'm having trouble logging into my computer. The system keeps giving me an error."
        ]
        
        for i, message in enumerate(test_messages, 1):
            print(f"   Test {i}: {message[:50]}...")
            result = router_ai.route_message(message)
            
            if "error" not in result:
                print(f"      ✅ Routed to: {result['department']}")
                print(f"      📋 Details: {result['details']}")
            else:
                print(f"      ❌ Error: {result['error']}")
        
        # Test 4: Check existing requests
        print("\n4️⃣ Testing Request System...")
        requests = Request.query.all()
        print(f"   ✅ Found {len(requests)} existing requests")
        
        if requests:
            for req in requests:
                print(f"   📝 Request #{req.id}: {req.title}")
                print(f"      Status: {req.status}")
                print(f"      Department: {req.department}")
                print(f"      Submitter: {req.submitter.username}")
        
        # Test 5: Check approval history
        print("\n5️⃣ Testing Approval History...")
        approvals = RequestApproval.query.all()
        print(f"   ✅ Found {len(approvals)} approval records")
        
        if approvals:
            for approval in approvals:
                approver = User.query.get(approval.approver_id)
                print(f"   ✅ Approval #{approval.id}: {approver.username} {approval.action}ed")
                print(f"      Level: {approval.approval_level}")
                print(f"      Comments: {approval.comments or 'None'}")
        
        print("\n🎉 Approval Workflow System Test Completed!")
        print("\n💡 Next Steps:")
        print("   1. Run the Flask app: python app.py")
        print("   2. Login with test credentials")
        print("   3. Submit a new request as an employee")
        print("   4. Approve/reject as department approver")
        print("   5. Final approval as admin")

def test_router_ai_integration():
    """Test Router AI integration specifically"""
    print("\n🤖 Testing Router AI Integration")
    print("=" * 40)
    
    # Test the company assistant prompt
    print(f"Company Assistant Prompt Length: {len(router_ai.company_assistant_prompt)} characters")
    print(f"Contains HR department info: {'Yes' if 'HR' in router_ai.company_assistant_prompt else 'No'}")
    print(f"Contains Sales department info: {'Yes' if 'Sales' in router_ai.company_assistant_prompt else 'No'}")
    print(f"Contains JSON format instructions: {'Yes' if 'JSON' in router_ai.company_assistant_prompt else 'No'}")
    
    # Test message routing
    test_message = "I need to request vacation time for next week"
    print(f"\nTesting message: '{test_message}'")
    
    result = router_ai.route_message(test_message)
    if "error" not in result:
        print(f"✅ Successfully routed to: {result['department']}")
        print(f"📋 Extracted details: {result['details']}")
        print(f"👤 Employee mentioned: {result['employee']}")
        print(f"📅 Dates mentioned: {result['dates']}")
    else:
        print(f"❌ Routing failed: {result['error']}")

if __name__ == "__main__":
    try:
        test_approval_workflow()
        test_router_ai_integration()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

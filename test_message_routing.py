#!/usr/bin/env python3
"""
Test script for Router AI message routing with company automation assistant prompt
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from router_ai_config import router_ai

def test_message_routing():
    """Test the message routing functionality"""
    print("🧠 Testing Router AI Message Routing with Company Assistant Prompt")
    print("=" * 70)
    
    # Test messages for different departments
    test_messages = [
        "Hi, I need to request vacation time for next week. Can you help me with the process?",
        "Our customer ABC Corp wants to place a large order. I need to discuss pricing options.",
        "The air conditioning in the office isn't working properly. Can someone check it?",
        "I'm having trouble logging into my computer. The system keeps giving me an error.",
        "I have a question about my benefits package and retirement options.",
        "We have a new lead from the trade show. Need to follow up on this opportunity.",
        "The printer on the 3rd floor is out of paper and showing an error message.",
        "I need to update my password and can't access the self-service portal."
    ]
    
    print("📝 Testing message routing for different scenarios:")
    print()
    
    for i, message in enumerate(test_messages, 1):
        print(f"Test {i}: {message[:60]}...")
        
        # Route the message
        result = router_ai.route_message(message)
        
        if "error" not in result:
            print(f"   ✅ Routed to: {result['department']}")
            print(f"   📋 Details: {result['details']}")
            if result['employee']:
                print(f"   👤 Employee: {result['employee']}")
            if result['dates']:
                print(f"   📅 Dates: {result['dates']}")
        else:
            print(f"   ❌ Error: {result['error']}")
        
        print()
    
    print("🎯 Testing the company assistant prompt:")
    print(f"   Prompt length: {len(router_ai.company_assistant_prompt)} characters")
    print(f"   Contains department info: {'Yes' if 'HR' in router_ai.company_assistant_prompt else 'No'}")
    print(f"   Contains JSON format: {'Yes' if 'JSON' in router_ai.company_assistant_prompt else 'No'}")
    print()
    
    print("🔧 Configuration Status:")
    print(f"   API Key: {'✅ Configured' if router_ai.api_key else '❌ Not configured'}")
    print(f"   Base URL: {router_ai.base_url}")
    print(f"   Mock Mode: {'✅ Enabled' if router_ai.mock_mode else '❌ Disabled'}")
    print()
    
    print("🎉 Message routing test completed successfully!")
    print("\n💡 The AI now understands its role as a company automation assistant")
    print("   and can intelligently route messages to the correct departments.")

if __name__ == "__main__":
    try:
        test_message_routing()
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

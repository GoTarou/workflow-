from router_ai_config import RouterAIConfig

# Test the Google Gemini AI integration
print("🧪 Testing Google Gemini AI Integration...")
print("=" * 50)

router_ai = RouterAIConfig()

test_messages = [
    "I need vacation time next week for a family trip",
    "My computer won't turn on and I can't access my files",
    "The air conditioning in the office is broken",
    "Customer ABC Corp wants to place a large order"
]

for message in test_messages:
    print(f"\n📝 Message: {message}")
    print("🤖 Calling Gemini AI...")
    
    try:
        result = router_ai.route_message(message)
        
        if "error" in result:
            print(f"   ❌ Error: {result['error']}")
        else:
            print(f"   ✅ Department: {result.get('department', 'Unknown')}")
            print(f"   ✅ Priority: {result.get('priority', 'Unknown')}")
            print(f"   ✅ Details: {result.get('details', 'Unknown')}")
            
    except Exception as e:
        print(f"   ❌ Exception: {str(e)}")
    
    print("-" * 40)

print("\n✅ Google Gemini AI integration test completed!")

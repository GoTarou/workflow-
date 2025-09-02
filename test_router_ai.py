#!/usr/bin/env python3
"""
Test script for Router AI integration
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from router_ai_config import router_ai

def test_router_ai_config():
    """Test the Router AI configuration"""
    print("Testing Router AI Configuration...")
    
    # Test API key
    print(f"API Key configured: {'Yes' if router_ai.api_key else 'No'}")
    print(f"Base URL: {router_ai.base_url}")
    
    # Test headers
    headers = router_ai.get_headers()
    print(f"Headers: {headers}")
    
    print("Router AI configuration test completed successfully!")

def test_document_analysis():
    """Test document analysis with a sample file"""
    print("\nTesting Document Analysis...")
    
    # Check if there's a sample document in uploads folder
    uploads_dir = "uploads"
    if os.path.exists(uploads_dir):
        files = [f for f in os.listdir(uploads_dir) if f.endswith(('.pdf', '.txt', '.doc', '.docx'))]
        if files:
            sample_file = os.path.join(uploads_dir, files[0])
            print(f"Found sample file: {sample_file}")
            
            # Test text extraction
            print("Testing text extraction...")
            result = router_ai.extract_text(sample_file)
            if "error" not in result:
                print("✓ Text extraction successful")
                print(f"  Result keys: {list(result.keys())}")
            else:
                print(f"✗ Text extraction failed: {result['error']}")
            
            # Test classification
            print("Testing document classification...")
            result = router_ai.classify_document(sample_file)
            if "error" not in result:
                print("✓ Classification successful")
                print(f"  Result keys: {list(result.keys())}")
            else:
                print(f"✗ Classification failed: {result['error']}")
            
            # Test summarization
            print("Testing document summarization...")
            result = router_ai.summarize_document(sample_file)
            if "error" not in result:
                print("✓ Summarization successful")
                print(f"  Result keys: {list(result.keys())}")
            else:
                print(f"✗ Summarization failed: {result['error']}")
        else:
            print("No sample documents found in uploads folder")
    else:
        print("Uploads folder not found")

if __name__ == "__main__":
    print("Router AI Integration Test")
    print("=" * 40)
    
    try:
        test_router_ai_config()
        test_document_analysis()
        print("\nAll tests completed!")
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()

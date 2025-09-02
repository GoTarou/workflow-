#!/usr/bin/env python3
"""
Demo script for Router AI integration
Shows how to use the Router AI functionality programmatically
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from router_ai_config import router_ai

def demo_document_analysis():
    """Demonstrate document analysis capabilities"""
    print("🚀 Router AI Integration Demo")
    print("=" * 50)
    
    # Check for sample documents
    uploads_dir = "uploads"
    if not os.path.exists(uploads_dir):
        print("❌ Uploads folder not found. Please create it and add some documents.")
        return
    
    files = [f for f in os.listdir(uploads_dir) if f.endswith(('.pdf', '.txt', '.doc', '.docx'))]
    if not files:
        print("❌ No documents found in uploads folder. Please add some documents first.")
        return
    
    sample_file = os.path.join(uploads_dir, files[0])
    print(f"📄 Using sample document: {files[0]}")
    print()
    
    # Demo 1: Quick Analysis
    print("🔍 Demo 1: Quick Analysis")
    print("-" * 30)
    result = router_ai.analyze_document(sample_file, "general")
    if "error" not in result:
        print("✅ Analysis successful!")
        print(f"   Document: {result['document_info']['filename']}")
        print(f"   Type: {result['document_info']['analysis_type']}")
        print(f"   Summary: {result['summary'][:100]}...")
        print(f"   Category: {result['classification']['category']}")
        print(f"   Confidence: {result['classification']['confidence']}")
    else:
        print(f"❌ Analysis failed: {result['error']}")
    print()
    
    # Demo 2: Text Extraction
    print("📝 Demo 2: Text Extraction")
    print("-" * 30)
    result = router_ai.extract_text(sample_file)
    if "error" not in result:
        print("✅ Text extraction successful!")
        print(f"   Document: {result['document']}")
        print(f"   Text length: {result['text_length']} characters")
        print(f"   Formatting preserved: {result['formatting_preserved']}")
        print(f"   Tables extracted: {result['tables_extracted']}")
        print(f"   Sample text: {result['extracted_text'][:100]}...")
    else:
        print(f"❌ Text extraction failed: {result['error']}")
    print()
    
    # Demo 3: Document Summarization
    print("📊 Demo 3: Document Summarization")
    print("-" * 30)
    for length in ["short", "medium", "long"]:
        result = router_ai.summarize_document(sample_file, length)
        if "error" not in result:
            print(f"✅ {length.title()} summary successful!")
            print(f"   Length: {result['summary_length']}")
            print(f"   Summary: {result['summary'][:80]}...")
            print(f"   Key points: {len(result['key_points'])} points")
        else:
            print(f"❌ {length.title()} summary failed: {result['error']}")
        print()
    
    # Demo 4: Document Classification
    print("🏷️  Demo 4: Document Classification")
    print("-" * 30)
    result = router_ai.classify_document(sample_file)
    if "error" not in result:
        print("✅ Classification successful!")
        print(f"   Document: {result['document']}")
        print(f"   Primary category: {result['classification']['primary_category']}")
        print(f"   Confidence: {result['classification']['confidence']}")
        print(f"   Subcategories: {', '.join(result['classification']['subcategories'])}")
        print(f"   Tags: {', '.join(result['classification']['tags'])}")
        print(f"   Suggested workflow: {result['classification']['suggested_workflow']}")
    else:
        print(f"❌ Classification failed: {result['error']}")
    print()
    
    # Demo 5: API Configuration
    print("⚙️  Demo 5: API Configuration")
    print("-" * 30)
    print(f"   API Key: {'✅ Configured' if router_ai.api_key else '❌ Not configured'}")
    print(f"   Base URL: {router_ai.base_url}")
    print(f"   Mock Mode: {'✅ Enabled' if router_ai.mock_mode else '❌ Disabled'}")
    print(f"   Headers: {router_ai.get_headers()}")
    print()
    
    print("🎉 Demo completed successfully!")
    print("\n💡 To use with real Router AI API:")
    print("   1. Set mock_mode = False in router_ai_config.py")
    print("   2. Ensure your API key is valid")
    print("   3. Verify the API endpoints are accessible")

if __name__ == "__main__":
    try:
        demo_document_analysis()
    except Exception as e:
        print(f"❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

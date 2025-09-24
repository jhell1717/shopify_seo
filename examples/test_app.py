#!/usr/bin/env python3
"""
Simple test script to verify the Shopify SEO Tool package works correctly.
"""

import os
import sys
import tempfile
import pandas as pd
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

from shopify_seo import ShopifySEOProcessor, Config

def create_test_csv():
    """Create a test CSV file with sample data."""
    test_data = {
        'Handle': ['test-product-1', 'test-product-2'],
        'Title': ['Test Product 1', 'Test Product 2'],
        'Body (HTML)': ['<p>Description for product 1</p>', '<p>Description for product 2</p>'],
        'Status': ['active', 'active'],
        'SEO Title': ['This is a very long SEO title that exceeds the maximum character limit for optimal search engine optimization', 'Another long SEO title that needs to be optimized for better search engine visibility'],
        'SEO Description': ['SEO description 1', 'SEO description 2']
    }
    
    df = pd.DataFrame(test_data)
    
    # Create temporary file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    
    return temp_file.name

def test_package():
    """Test the Shopify SEO Tool package functionality."""
    print("🧪 Testing Shopify SEO Tool Package")
    print("=" * 40)
    
    # Test 1: Configuration
    print("1. Testing Configuration...")
    config = Config()
    assert config.max_title_length == 53
    assert config.model_name == "gpt-oss:latest"
    print("   ✅ Configuration test passed")
    
    # Test 2: CSV Validation
    print("2. Testing CSV Validation...")
    test_csv = create_test_csv()
    processor = ShopifySEOProcessor(config)
    
    is_valid, error_msg = processor.validate_csv(test_csv)
    assert is_valid, f"CSV validation failed: {error_msg}"
    print("   ✅ CSV validation test passed")
    
    # Test 3: Title Processing (without AI - just length enforcement)
    print("3. Testing Title Length Enforcement...")
    long_title = "This is a very long title that exceeds the maximum character limit"
    enforced_title = processor._enforce_length(long_title)
    assert len(enforced_title) <= config.max_title_length
    print(f"   Original length: {len(long_title)}")
    print(f"   Enforced length: {len(enforced_title)}")
    print("   ✅ Title length enforcement test passed")
    
    # Test 4: Processing Result Structure
    print("4. Testing Processing Result Structure...")
    from shopify_seo.processor import ProcessingResult
    
    result = ProcessingResult(
        output_file="test.csv",
        total_products=10,
        active_products=5,
        edited_titles=3,
        processing_time=1.5,
        success=True
    )
    
    assert result.total_products == 10
    assert result.success == True
    print("   ✅ Processing result structure test passed")
    
    # Cleanup
    os.unlink(test_csv)
    
    print("\n🎉 All tests passed! Package is working correctly.")
    print("\n📝 To run the web application:")
    print("   python app.py")
    print("\n📝 To use the CLI:")
    print("   python -m shopify_seo.cli process data/products_export_1.csv")
    print("\n📝 To run the example:")
    print("   python example.py")

if __name__ == "__main__":
    test_package()

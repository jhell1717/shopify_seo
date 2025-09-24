#!/usr/bin/env python3
"""
Example usage of the Shopify SEO Tool package.
"""

from shopify_seo import ShopifySEOProcessor, Config

def main():
    """Example usage of the Shopify SEO Tool."""
    
    # Example 1: Using default configuration
    print("🚀 Example 1: Using default configuration")
    processor = ShopifySEOProcessor()
    
    # Validate a CSV file
    input_file = "/Users/joshuahellewell/Desktop/01-dev/shopify_app/data/products_export_1 copy.csv"
    is_valid, error_msg = processor.validate_csv(input_file)
    
    if is_valid:
        print(f"✅ CSV file is valid: {input_file}")
        
        # Process the file
        result = processor.process_csv(input_file)
        
        if result.success:
            print(f"📊 Processing Results:")
            print(f"   Total products: {result.total_products}")
            print(f"   Active products: {result.active_products}")
            print(f"   Titles edited: {result.edited_titles}")
            print(f"   Processing time: {result.processing_time:.2f} seconds")
            print(f"   Output file: {result.output_file}")
        else:
            print(f"❌ Processing failed: {result.error_message}")
    else:
        print(f"❌ CSV validation failed: {error_msg}")
    
    print("\n" + "="*50 + "\n")
    
    # Example 2: Using custom configuration
    print("🚀 Example 2: Using custom configuration")
    config = Config(
        model_name="gpt-oss:latest",
        max_title_length=60,
        temp_dir="custom_temp"
    )
    
    processor_custom = ShopifySEOProcessor(config)
    
    print(f"🔧 Custom configuration:")
    print(f"   Model: {config.model_name}")
    print(f"   Max title length: {config.max_title_length}")
    print(f"   Temp directory: {config.temp_dir}")
    
    # Example 3: Process with custom output file
    print("\n🚀 Example 3: Process with custom output file")
    output_file = "/Users/joshuahellewell/Desktop/01-dev/shopify_app/data/products_optimized_custom.csv"
    result = processor_custom.process_csv(input_file, output_file)
    
    if result.success:
        print(f"✅ Custom processing completed!")
        print(f"   Output saved to: {result.output_file}")
    else:
        print(f"❌ Custom processing failed: {result.error_message}")

if __name__ == "__main__":
    main()

"""
Command-line interface for Shopify SEO Tool.
"""

import argparse
import sys
import os
from pathlib import Path

from .processor import ShopifySEOProcessor
from .config import Config


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Shopify SEO Tool - AI-powered product title optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  shopify-seo process products.csv
  shopify-seo process products.csv -o optimized_products.csv
  shopify-seo process products.csv --max-length 60
  shopify-seo validate products.csv
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Process command
    process_parser = subparsers.add_parser('process', help='Process a Shopify CSV file')
    process_parser.add_argument('input_file', help='Input CSV file path')
    process_parser.add_argument('-o', '--output', help='Output CSV file path')
    process_parser.add_argument('--max-length', type=int, default=53,
                               help='Maximum title length (default: 53)')
    process_parser.add_argument('--model', default='gpt-oss:latest',
                               help='AI model name (default: gpt-oss:latest)')
    process_parser.add_argument('--temp-dir', default='temp',
                               help='Temporary directory (default: temp)')
    process_parser.add_argument('--verbose', '-v', action='store_true',
                               help='Verbose output')
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate a CSV file')
    validate_parser.add_argument('input_file', help='Input CSV file path')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show current configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'process':
            process_command(args)
        elif args.command == 'validate':
            validate_command(args)
        elif args.command == 'config':
            config_command(args)
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


def process_command(args):
    """Handle the process command."""
    input_file = Path(args.input_file)
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)
    
    # Create configuration
    config = Config(
        model_name=args.model,
        max_title_length=args.max_length,
        temp_dir=args.temp_dir
    )
    
    # Initialize processor
    processor = ShopifySEOProcessor(config)
    
    if args.verbose:
        print(f"🔧 Configuration:")
        print(f"   Model: {config.model_name}")
        print(f"   Max title length: {config.max_title_length}")
        print(f"   Temp directory: {config.temp_dir}")
        print()
    
    print(f"📁 Processing file: {input_file}")
    
    # Process the file
    result = processor.process_csv(str(input_file), args.output)
    
    if result.success:
        print(f"✅ Processing completed successfully!")
        print(f"📊 Statistics:")
        print(f"   Total products: {result.total_products}")
        print(f"   Active products: {result.active_products}")
        print(f"   Titles edited: {result.edited_titles}")
        print(f"   Processing time: {result.processing_time:.2f} seconds")
        print(f"📄 Output file: {result.output_file}")
    else:
        print(f"❌ Processing failed: {result.error_message}")
        sys.exit(1)


def validate_command(args):
    """Handle the validate command."""
    input_file = Path(args.input_file)
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)
    
    processor = ShopifySEOProcessor()
    is_valid, error_message = processor.validate_csv(str(input_file))
    
    if is_valid:
        print(f"✅ CSV file is valid: {input_file}")
    else:
        print(f"❌ CSV file validation failed: {error_message}")
        sys.exit(1)


def config_command(args):
    """Handle the config command."""
    config = Config.from_env()
    
    print("🔧 Current Configuration:")
    print(f"   Model name: {config.model_name}")
    print(f"   Max title length: {config.max_title_length}")
    print(f"   Temp directory: {config.temp_dir}")
    print(f"   Allowed extensions: {config.allowed_extensions}")
    print(f"   Max file size: {config.max_file_size / (1024*1024):.1f} MB")
    print(f"   API timeout: {config.api_timeout} seconds")
    print(f"   Max retries: {config.max_retries}")
    print()
    print("💡 Set environment variables to override defaults:")
    print("   SHOPIFY_SEO_MODEL")
    print("   SHOPIFY_SEO_MAX_TITLE_LENGTH")
    print("   SHOPIFY_SEO_TEMP_DIR")
    print("   SHOPIFY_SEO_API_TIMEOUT")
    print("   SHOPIFY_SEO_MAX_RETRIES")

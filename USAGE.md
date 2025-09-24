# Shopify SEO Tool - Usage Guide

## 🚀 Quick Start

Your Shopify SEO tool has been successfully transformed into a Python package with OOP design and a Flask web application!

## 📁 Project Structure

```
shopify_app/
├── shopify_seo/              # Python package
│   ├── __init__.py          # Package initialization
│   ├── config.py            # Configuration management
│   ├── processor.py         # Main SEO processor class
│   └── cli.py              # Command-line interface
├── app.py                   # Flask web application
├── requirements.txt         # Dependencies
├── setup.py                # Package setup
├── example.py              # Usage examples
├── test_app.py             # Test suite
├── env.example             # Environment variables template
└── data/                   # Your CSV files
    └── products_export_1.csv
```

## 🌐 Web Application

### Start the Web App
```bash
cd /Users/joshuahellewell/Desktop/01-dev/shopify_app
python app.py
```

Then open your browser to: `http://localhost:5000`

### Features:
- ✅ Drag & drop CSV file upload
- ✅ Real-time processing progress
- ✅ Beautiful, modern UI
- ✅ Download optimized CSV files
- ✅ Processing statistics

## 🐍 Python Package Usage

### Install the Package
```bash
pip install -e .
```

### Basic Usage
```python
from shopify_seo import ShopifySEOProcessor, Config

# Initialize processor
processor = ShopifySEOProcessor()

# Process a CSV file
result = processor.process_csv('data/products_export_1.csv')

if result.success:
    print(f"✅ Processed {result.total_products} products")
    print(f"📝 Edited {result.edited_titles} titles")
    print(f"⏱️ Processing time: {result.processing_time:.2f}s")
    print(f"📄 Output: {result.output_file}")
```

### Advanced Configuration
```python
from shopify_seo import ShopifySEOProcessor, Config

# Custom configuration
config = Config(
    model_name="gpt-oss:latest",
    max_title_length=60,
    temp_dir="my_temp_folder"
)

processor = ShopifySEOProcessor(config)
```

## 🖥️ Command Line Interface

### Process a CSV file
```bash
python -m shopify_seo.cli process data/products_export_1.csv
```

### Process with custom output
```bash
python -m shopify_seo.cli process data/products_export_1.csv -o optimized_products.csv
```

### Validate a CSV file
```bash
python -m shopify_seo.cli validate data/products_export_1.csv
```

### Show configuration
```bash
python -m shopify_seo.cli config
```

### Help
```bash
python -m shopify_seo.cli --help
```

## ⚙️ Configuration

### Environment Variables
Create a `.env` file (copy from `env.example`):
```bash
cp env.example .env
```

Available variables:
- `SHOPIFY_SEO_MODEL`: AI model name (default: "gpt-oss:latest")
- `SHOPIFY_SEO_MAX_TITLE_LENGTH`: Maximum title length (default: 53)
- `SHOPIFY_SEO_TEMP_DIR`: Temporary directory (default: "temp")
- `SHOPIFY_SEO_API_TIMEOUT`: API timeout in seconds (default: 30)

## 🔧 API Endpoints

### Web Interface
- `GET /`: Main web application
- `POST /api/upload`: Upload and process CSV
- `GET /api/download/<job_id>`: Download processed file
- `GET /api/status/<job_id>`: Get processing status
- `GET /api/health`: Health check

### Example API Usage
```bash
# Upload file
curl -X POST -F "file=@data/products_export_1.csv" http://localhost:5000/api/upload

# Download processed file
curl -O http://localhost:5000/api/download/<job_id>
```

## 🧪 Testing

Run the test suite:
```bash
python test_app.py
```

Run the example:
```bash
python example.py
```

## 📊 CSV Requirements

Your Shopify CSV export must contain these columns:
- `Title`: Product title
- `Body (HTML)`: Product description  
- `Status`: Product status (active, draft, etc.)
- `SEO Title`: SEO-optimized title (will be edited)
- `SEO Description`: SEO description

## 🎯 Key Features

### Object-Oriented Design
- `ShopifySEOProcessor`: Main processing class
- `Config`: Configuration management
- `ProcessingResult`: Result data structure

### Error Handling
- Robust CSV validation
- Graceful error recovery
- Detailed error messages

### Performance
- Batch processing
- Progress tracking
- Memory efficient

### Security
- File size limits
- Temporary file cleanup
- Input validation

## 🚀 Next Steps

1. **Start the web app**: `python app.py`
2. **Upload your CSV**: Use the web interface
3. **Download results**: Get your optimized CSV
4. **Import to Shopify**: Upload the optimized file

## 🆘 Troubleshooting

### Common Issues

1. **Import errors**: Make sure you've installed dependencies
   ```bash
   pip install -r requirements.txt
   ```

2. **CSV validation errors**: Check that your CSV has required columns

3. **Processing errors**: Ensure Ollama is running with the correct model

4. **File size errors**: Large files may take longer to process

### Getting Help

- Check the console output for detailed error messages
- Verify your CSV file format
- Ensure all dependencies are installed
- Check that Ollama is running

## 🎉 Success!

Your Shopify SEO tool is now a professional Python package with:
- ✅ Object-oriented architecture
- ✅ Flask web application
- ✅ Command-line interface
- ✅ Comprehensive error handling
- ✅ Beautiful user interface
- ✅ API endpoints
- ✅ Package management
- ✅ Documentation

Enjoy optimizing your Shopify product titles! 🚀

# Shopify SEO Tool

An AI-powered Python package and web application for optimizing Shopify product titles using advanced language models. This tool helps e-commerce businesses improve their SEO by automatically rewriting product titles to be more concise, descriptive, and search-engine friendly.

## Features

- 🤖 **AI-Powered Title Optimisation**: Uses advanced language models to rewrite product titles
- **Batch Processing**: Process entire Shopify CSV exports efficiently
- **SEO-Focused**: Optimizes titles for search engines while maintaining readability
- **Web Interface**: Easy-to-use web application with drag-and-drop file upload
- **Python Package**: Use as a library in your own applications
- **Fast Processing**: Optimized for handling large product catalogs
- **Secure**: Temporary file handling with automatic cleanup

## Installation

### From Source

```bash
git clone https://github.com/yourusername/shopify-seo-tool.git
cd shopify-seo-tool
pip install -r requirements.txt
```

### As a Package

```bash
pip install -e .
```

## Quick Start

### Web Application

1. Start the Flask application:
```bash
python app.py
```

2. Open your browser and go to `http://localhost:5000`

3. Upload your Shopify CSV file and download the optimized version

### Python Package Usage

```python
from shopify_seo import ShopifySEOProcessor, Config

# Initialize processor with default config
processor = ShopifySEOProcessor()

# Process a CSV file
result = processor.process_csv('products.csv', 'optimized_products.csv')

if result.success:
    print(f"Processed {result.total_products} products")
    print(f"Edited {result.edited_titles} titles")
    print(f"Processing time: {result.processing_time:.2f} seconds")
else:
    print(f"Error: {result.error_message}")
```

## Configuration

You can customize the behavior using environment variables or the Config class:

```python
from shopify_seo import Config

config = Config(
    model_name="gpt-oss:latest",
    max_title_length=60,
    temp_dir="my_temp_folder",
    api_timeout=60
)

processor = ShopifySEOProcessor(config)
```

### Environment Variables

- `SHOPIFY_SEO_MODEL`: AI model name (default: "gpt-oss:latest")
- `SHOPIFY_SEO_MAX_TITLE_LENGTH`: Maximum title length (default: 53)
- `SHOPIFY_SEO_TEMP_DIR`: Temporary directory for processing (default: "temp")
- `SHOPIFY_SEO_API_TIMEOUT`: API timeout in seconds (default: 30)
- `SHOPIFY_SEO_MAX_RETRIES`: Maximum retry attempts (default: 3)

## CSV Format Requirements

Your Shopify CSV export must contain the following columns:

- `Title`: Product title
- `Body (HTML)`: Product description
- `Status`: Product status (active, draft, etc.)
- `SEO Title`: SEO-optimized title (will be edited)
- `SEO Description`: SEO description

## API Endpoints

### Web Application

- `GET /`: Main web interface
- `POST /api/upload`: Upload and process CSV file
- `GET /api/download/<job_id>`: Download processed file
- `GET /api/status/<job_id>`: Get processing status
- `GET /api/health`: Health check

### Example API Usage

```bash
# Upload file
curl -X POST -F "file=@products.csv" http://localhost:5000/api/upload

# Download processed file
curl -O http://localhost:5000/api/download/<job_id>
```

## Architecture

The package is built with object-oriented design principles:

- `ShopifySEOProcessor`: Main processing class
- `Config`: Configuration management
- `ProcessingResult`: Result data structure
- Flask API: Web interface and REST endpoints

## Requirements

- Python 3.8+
- Ollama (for AI model)
- Flask
- Pandas
- Werkzeug

## Development

### Setup Development Environment

```bash
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black shopify_seo/
flake8 shopify_seo/
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the example usage

## Changelog

### v1.0.0
- Initial release
- AI-powered title optimisation
- Web interface
- Python package
- Batch processing support

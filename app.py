"""
Flask API for Shopify SEO Tool.
"""

import os
import uuid
from flask import Flask, request, jsonify, send_file, render_template
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

from shopify_seo import ShopifySEOProcessor, Config


app = Flask(__name__)

# Configuration
config = Config.from_env()
app.config['MAX_CONTENT_LENGTH'] = config.max_file_size
app.config['UPLOAD_FOLDER'] = config.temp_dir

# Ensure upload directory exists
os.makedirs(config.temp_dir, exist_ok=True)

# Initialize processor
processor = ShopifySEOProcessor(config)

# In-memory storage for processing results (in production, use Redis or database)
processing_results = {}


@app.route('/')
def index():
    """Serve the main web interface."""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Handle CSV file upload and processing."""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Only CSV files are allowed'}), 400
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        
        # Save uploaded file
        file.save(file_path)
        
        # Process the file
        result = processor.process_csv(file_path)
        
        # Store result for download
        job_id = str(uuid.uuid4())
        processing_results[job_id] = {
            'result': result,
            'original_filename': filename,
            'output_filename': os.path.basename(result.output_file) if result.success else None
        }
        
        # Clean up uploaded file
        os.remove(file_path)
        
        if result.success:
            return jsonify({
                'job_id': job_id,
                'message': 'File processed successfully',
                'stats': {
                    'total_products': int(result.total_products),
                    'active_products': int(result.active_products),
                    'edited_titles': int(result.edited_titles),
                    'processing_time': round(result.processing_time, 2)
                }
            }), 200
        else:
            return jsonify({'error': result.error_message}), 500
            
    except RequestEntityTooLarge:
        return jsonify({'error': 'File too large'}), 413
    except (OSError, ValueError, RuntimeError) as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<job_id>')
def download_file(job_id):
    """Download processed CSV file."""
    if job_id not in processing_results:
        return jsonify({'error': 'Job not found'}), 404
    
    job_data = processing_results[job_id]
    result = job_data['result']
    
    if not result.success:
        return jsonify({'error': 'Processing failed'}), 500
    
    if not os.path.exists(result.output_file):
        return jsonify({'error': 'Output file not found'}), 404
    
    return send_file(
        result.output_file,
        as_attachment=True,
        download_name=f"optimized_{job_data['original_filename']}",
        mimetype='text/csv'
    )


@app.route('/api/status/<job_id>')
def get_status(job_id):
    """Get processing status for a job."""
    if job_id not in processing_results:
        return jsonify({'error': 'Job not found'}), 404
    
    job_data = processing_results[job_id]
    result = job_data['result']
    
    return jsonify({
        'success': result.success,
        'stats': {
            'total_products': int(result.total_products),
            'active_products': int(result.active_products),
            'edited_titles': int(result.edited_titles),
            'processing_time': round(result.processing_time, 2)
        } if result.success else None,
        'error': result.error_message if not result.success else None
    })


@app.route('/api/health')
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'version': '1.0.0'})




if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5080)

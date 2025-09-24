"""
Flask API for Shopify SEO Tool.
"""

import os
import uuid
from flask import Flask, request, jsonify, send_file, render_template_string
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
    return render_template_string(HTML_TEMPLATE)


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


# HTML template for the web interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Shopify SEO Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 10px;
            font-size: 2.5em;
            font-weight: 700;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 40px;
            font-size: 1.1em;
        }
        
        .upload-area {
            border: 3px dashed #ddd;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            transition: all 0.3s ease;
            cursor: pointer;
            margin-bottom: 30px;
        }
        
        .upload-area:hover {
            border-color: #667eea;
            background-color: #f8f9ff;
        }
        
        .upload-area.dragover {
            border-color: #667eea;
            background-color: #f0f4ff;
        }
        
        .upload-icon {
            font-size: 3em;
            color: #667eea;
            margin-bottom: 20px;
        }
        
        .upload-text {
            font-size: 1.2em;
            color: #333;
            margin-bottom: 10px;
        }
        
        .upload-subtext {
            color: #666;
            font-size: 0.9em;
        }
        
        #fileInput {
            display: none;
        }
        
        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 50px;
            font-size: 1.1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
            margin-bottom: 20px;
        }
        
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }
        
        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        
        .progress {
            display: none;
            margin: 20px 0;
        }
        
        .progress-bar {
            background: #f0f0f0;
            border-radius: 10px;
            height: 8px;
            overflow: hidden;
        }
        
        .progress-fill {
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .status {
            display: none;
            padding: 15px;
            border-radius: 10px;
            margin: 20px 0;
            text-align: center;
        }
        
        .status.success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .status.error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        
        .stat {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
        }
        
        .stat-number {
            font-size: 1.5em;
            font-weight: bold;
            color: #667eea;
        }
        
        .stat-label {
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }
        
        .download-btn {
            background: #28a745;
            margin-top: 20px;
        }
        
        .download-btn:hover {
            background: #218838;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1> Shopify SEO Tool</h1>
        <p class="subtitle">Optimize your product titles with AI-powered SEO enhancement</p>
        
        <div class="upload-area" id="uploadArea">
            <div class="upload-icon">📁</div>
            <div class="upload-text">Drop your CSV file here or click to browse</div>
            <div class="upload-subtext">Maximum file size: 16MB</div>
            <input type="file" id="fileInput" accept=".csv" />
        </div>
        
        <button class="btn" id="processBtn" onclick="processFile()" disabled>
            Process File
        </button>
        
        <div class="progress" id="progress">
            <div class="progress-bar">
                <div class="progress-fill" id="progressFill"></div>
            </div>
            <div style="text-align: center; margin-top: 10px; color: #666;">
                Processing your file...
            </div>
        </div>
        
        <div class="status" id="status"></div>
    </div>

    <script>
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const processBtn = document.getElementById('processBtn');
        const progress = document.getElementById('progress');
        const progressFill = document.getElementById('progressFill');
        const status = document.getElementById('status');
        
        let selectedFile = null;
        let currentJobId = null;
        
        // File input handling
        uploadArea.addEventListener('click', () => fileInput.click());
        fileInput.addEventListener('change', handleFileSelect);
        
        // Drag and drop handling
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect({ target: { files: files } });
            }
        });
        
        function handleFileSelect(event) {
            const file = event.target.files[0];
            if (file) {
                if (file.type === 'text/csv' || file.name.endsWith('.csv')) {
                    selectedFile = file;
                    uploadArea.innerHTML = `
                        <div class="upload-icon">✅</div>
                        <div class="upload-text">${file.name}</div>
                        <div class="upload-subtext">Ready to process</div>
                        <input type="file" id="fileInput" accept=".csv" style="display: none;" />
                    `;
                    processBtn.disabled = false;
                } else {
                    showStatus('Please select a CSV file', 'error');
                }
            }
        }
        
        async function processFile() {
            if (!selectedFile) return;
            
            processBtn.disabled = true;
            progress.style.display = 'block';
            progressFill.style.width = '10%';
            status.style.display = 'none';
            
            const formData = new FormData();
            formData.append('file', selectedFile);
            
            try {
                progressFill.style.width = '30%';
                
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });
                
                progressFill.style.width = '70%';
                
                const data = await response.json();
                
                if (response.ok) {
                    currentJobId = data.job_id;
                    progressFill.style.width = '100%';
                    
                    setTimeout(() => {
                        showSuccess(data);
                    }, 500);
                } else {
                    showStatus(data.error || 'Processing failed', 'error');
                }
            } catch (error) {
                showStatus('Network error: ' + error.message, 'error');
            } finally {
                processBtn.disabled = false;
                progress.style.display = 'none';
            }
        }
        
        function showSuccess(data) {
            const stats = data.stats;
            status.innerHTML = `
                <div style="color: #155724; font-weight: bold; margin-bottom: 15px;">
                    ✅ Processing completed successfully!
                </div>
                <div class="stats">
                    <div class="stat">
                        <div class="stat-number">${stats.total_products}</div>
                        <div class="stat-label">Total Products</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">${stats.active_products}</div>
                        <div class="stat-label">Active Products</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">${stats.edited_titles}</div>
                        <div class="stat-label">Titles Edited</div>
                    </div>
                    <div class="stat">
                        <div class="stat-number">${stats.processing_time}s</div>
                        <div class="stat-label">Processing Time</div>
                    </div>
                </div>
                <button class="btn download-btn" onclick="downloadFile()">
                    📥 Download Optimized CSV
                </button>
            `;
            status.className = 'status success';
            status.style.display = 'block';
        }
        
        function showStatus(message, type) {
            status.innerHTML = message;
            status.className = `status ${type}`;
            status.style.display = 'block';
        }
        
        async function downloadFile() {
            if (!currentJobId) return;
            
            try {
                const response = await fetch(`/api/download/${currentJobId}`);
                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `optimized_${selectedFile.name}`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);
                } else {
                    showStatus('Download failed', 'error');
                }
            } catch (error) {
                showStatus('Download error: ' + error.message, 'error');
            }
        }
    </script>
</body>
</html>
"""


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5080)

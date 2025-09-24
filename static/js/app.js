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

// Core scanning functionality
class Scanner {
    constructor() {
        this.dropZone = document.getElementById('dropZone');
        this.fileInput = document.getElementById('fileInput');
        this.fileList = document.getElementById('fileList');
        this.progressSection = document.getElementById('progressSection');
        this.resultsSection = document.getElementById('resultsSection');
        this.scanProgress = document.getElementById('scanProgress');
        this.filesScanned = document.getElementById('filesScanned');
        this.threatsFound = document.getElementById('threatsFound');
        this.scanTime = document.getElementById('scanTime');
        this.scanTypes = document.querySelectorAll('.scan-type');
        
        this.files = [];
        this.currentScanType = 'malware';
        this.startTime = null;
        this.scanInterval = null;

        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // File Drop Zone Events
        this.dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            this.dropZone.classList.add('drag-over');
        });

        this.dropZone.addEventListener('dragleave', () => {
            this.dropZone.classList.remove('drag-over');
        });

        this.dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            this.dropZone.classList.remove('drag-over');
            const files = Array.from(e.dataTransfer.files);
            this.handleFiles(files);
        });

        this.dropZone.addEventListener('click', () => {
            this.fileInput.click();
        });

        this.fileInput.addEventListener('change', (e) => {
            const files = Array.from(e.target.files);
            this.handleFiles(files);
        });

        // Scan Type Selection
        this.scanTypes.forEach(type => {
            type.addEventListener('click', () => {
                this.scanTypes.forEach(t => t.classList.remove('active'));
                type.classList.add('active');
                this.currentScanType = type.dataset.type;
            });
        });
    }

    handleFiles(newFiles) {
        // Validate files
        const validFiles = newFiles.filter(file => {
            const maxSize = 50 * 1024 * 1024; // 50MB
            if (file.size > maxSize) {
                this.showError(`File ${file.name} is too large. Maximum size is 50MB.`);
                return false;
            }
            return true;
        });

        // Add valid files to the list
        this.files.push(...validFiles);
        this.updateFileList();
    }

    updateFileList() {
        this.fileList.innerHTML = '';
        
        this.files.forEach((file, index) => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <i class="fas ${this.getFileIcon(file)} file-icon"></i>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-meta">${this.formatFileSize(file.size)}</div>
                </div>
                <div class="file-actions">
                    <button class="btn btn-icon" onclick="scanner.removeFile(${index})">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            `;
            this.fileList.appendChild(fileItem);
        });

        // Show/hide scan button based on file count
        if (this.files.length > 0) {
            this.showScanButton();
        } else {
            this.hideScanButton();
        }
    }

    getFileIcon(file) {
        const type = file.type.split('/')[0];
        switch (type) {
            case 'image': return 'fa-image';
            case 'video': return 'fa-video';
            case 'audio': return 'fa-music';
            case 'application': return 'fa-file-alt';
            default: return 'fa-file';
        }
    }

    formatFileSize(bytes) {
        const units = ['B', 'KB', 'MB', 'GB'];
        let size = bytes;
        let unitIndex = 0;
        
        while (size >= 1024 && unitIndex < units.length - 1) {
            size /= 1024;
            unitIndex++;
        }

        return `${size.toFixed(1)} ${units[unitIndex]}`;
    }

    removeFile(index) {
        this.files.splice(index, 1);
        this.updateFileList();
    }

    showScanButton() {
        const scanBtn = document.createElement('button');
        scanBtn.className = 'btn btn-primary mt-4 w-100';
        scanBtn.innerHTML = '<i class="fas fa-shield-alt"></i> Start Scan';
        scanBtn.onclick = () => this.startScan();
        
        if (!document.querySelector('.scan-button')) {
            this.fileList.appendChild(scanBtn);
        }
    }

    hideScanButton() {
        const scanBtn = document.querySelector('.scan-button');
        if (scanBtn) {
            scanBtn.remove();
        }
    }

    async startScan() {
        this.startTime = Date.now();
        this.progressSection.style.display = 'block';
        this.updateProgress(0);
        this.updateStats(0, 0);
        this.startTimer();

        // Prepare form data
        const formData = new FormData();
        this.files.forEach(file => {
            formData.append('files[]', file);
        });
        formData.append('scan_type', this.currentScanType);

        try {
            const response = await fetch('/api/scan', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error('Scan failed');
            }

            const results = await response.json();
            this.showResults(results);
        } catch (error) {
            this.showError('Scan failed: ' + error.message);
        } finally {
            clearInterval(this.scanInterval);
        }
    }

    updateProgress(percent) {
        this.scanProgress.style.width = `${percent}%`;
    }

    updateStats(scanned, threats) {
        this.filesScanned.textContent = scanned;
        this.threatsFound.textContent = threats;
    }

    startTimer() {
        clearInterval(this.scanInterval);
        this.scanInterval = setInterval(() => {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            this.scanTime.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
        }, 1000);
    }

    showResults(results) {
        this.resultsSection.style.display = 'block';
        const resultsGrid = document.getElementById('resultsGrid');
        resultsGrid.innerHTML = '';

        results.forEach(result => {
            const resultCard = document.createElement('div');
            resultCard.className = 'result-card';
            resultCard.innerHTML = `
                <div class="result-header">
                    <div>
                        <h3 class="result-title">${result.filename}</h3>
                        <div class="result-meta">${this.formatFileSize(result.size)}</div>
                    </div>
                    <span class="result-status status-${result.status === 'clean' ? 'clean' : 'threat'}">
                        ${result.status}
                    </span>
                </div>
                <div class="result-details">
                    <div class="detail-item">
                        <span class="detail-label">Scan Type</span>
                        <span class="detail-value">${result.scan_type}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Confidence</span>
                        <span class="detail-value">${result.confidence}%</span>
                    </div>
                    ${result.threats ? `
                    <div class="detail-item">
                        <span class="detail-label">Threats Found</span>
                        <span class="detail-value">${result.threats.join(', ')}</span>
                    </div>
                    ` : ''}
                </div>
            `;
            resultsGrid.appendChild(resultCard);
        });
    }

    showError(message) {
        // Implement error notification
        console.error(message);
    }
}

// Initialize Scanner
const scanner = new Scanner();

// Export Results Function
function exportResults() {
    // Implement export functionality
    console.log('Exporting results...');
}

// Export the Scanner class
export default Scanner;

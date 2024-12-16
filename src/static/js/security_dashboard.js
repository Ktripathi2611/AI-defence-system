// Threat Detection Functions
async function scanForThreats() {
    const urlInput = document.getElementById('urlInput').value;
    if (!urlInput) {
        showNotification('Please enter a URL or file path', 'error');
        return;
    }

    try {
        showNotification('Scanning for threats...', 'info');
        const response = await fetch('/api/scan/threat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ target: urlInput })
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        if (data.error) {
            showNotification(data.error, 'error');
        } else {
            updateThreatResults(data.result);
            showNotification('Scan completed successfully', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error during threat scan: ' + error.message, 'error');
    }
}

function updateThreatResults(result) {
    const resultsDiv = document.getElementById('threatResults');
    if (!result) {
        resultsDiv.innerHTML = '<p class="text-gray-600">No results available</p>';
        return;
    }

    const confidence = (result.confidence * 100).toFixed(1);
    const statusClass = result.status === 'malicious' ? 'text-red-600' : 'text-green-600';
    const iconClass = result.status === 'malicious' ? 'fa-exclamation-triangle' : 'fa-check-circle';

    resultsDiv.innerHTML = `
        <div class="p-4 bg-white rounded-lg shadow">
            <div class="flex items-center mb-2">
                <i class="fas ${iconClass} ${statusClass} mr-2"></i>
                <span class="font-semibold ${statusClass} capitalize">${result.status}</span>
            </div>
            <div class="text-sm text-gray-600">
                <p>Confidence: ${confidence}%</p>
                ${result.details ? `<p class="mt-1">${result.details}</p>` : ''}
            </div>
        </div>
    `;
}

// DeepFake Analysis Functions
function handleDrop(event) {
    event.preventDefault();
    const files = event.dataTransfer.files;
    handleFiles(files);
}

function handleDragOver(event) {
    event.preventDefault();
}

function triggerFileUpload() {
    document.getElementById('fileInput').click();
}

function handleFileSelect(event) {
    const files = event.target.files;
    handleFiles(files);
}

async function handleFiles(files) {
    if (files.length === 0) return;

    const file = files[0];
    const formData = new FormData();
    formData.append('file', file);

    try {
        showNotification('Analyzing media...', 'info');
        const response = await fetch('/api/analyze/deepfake', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        if (data.error) {
            showNotification(data.error, 'error');
        } else {
            updateAnalysisResults(data.result);
            showNotification('Analysis completed successfully', 'success');
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification('Error during analysis: ' + error.message, 'error');
    }
}

function updateAnalysisResults(result) {
    const resultsDiv = document.getElementById('analysisResults');
    if (!result) {
        resultsDiv.innerHTML = '<p class="text-gray-600">No results available</p>';
        return;
    }

    const confidence = (result.confidence * 100).toFixed(1);
    const isDeepfake = result.confidence > 0.7;
    const statusClass = isDeepfake ? 'text-red-600' : 'text-green-600';
    const iconClass = isDeepfake ? 'fa-exclamation-triangle' : 'fa-check-circle';

    resultsDiv.innerHTML = `
        <div class="p-4 bg-white rounded-lg shadow">
            <div class="flex items-center mb-2">
                <i class="fas ${iconClass} ${statusClass} mr-2"></i>
                <span class="font-semibold ${statusClass}">${isDeepfake ? 'DeepFake Detected' : 'Authentic Media'}</span>
            </div>
            <div class="text-sm text-gray-600">
                <p>Confidence: ${confidence}%</p>
                ${result.details ? `<p class="mt-1">${result.details}</p>` : ''}
            </div>
        </div>
    `;
}

// Security Overview Functions
async function loadSecurityStatus() {
    try {
        const response = await fetch('/api/security/status');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        updateSecurityStatus(data);
    } catch (error) {
        console.error('Error loading security status:', error);
        showNotification('Error loading security status', 'error');
    }
}

// Recent Activity Functions
async function loadRecentActivity() {
    try {
        const response = await fetch('/api/security/activity');
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        updateActivityFeed(data.activities);
    } catch (error) {
        console.error('Error loading recent activity:', error);
        showNotification('Error loading recent activity', 'error');
    }
}

function updateActivityFeed(activities) {
    const feedDiv = document.getElementById('activityFeed');
    if (!activities || activities.length === 0) {
        feedDiv.innerHTML = '<p class="text-gray-600">No recent activity</p>';
        return;
    }

    const activityHTML = activities.map(activity => `
        <div class="flex items-start space-x-3 p-3 hover:bg-gray-50 rounded-lg">
            <div class="flex-shrink-0">
                <i class="fas ${getActivityIcon(activity.type)} text-blue-500"></i>
            </div>
            <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900">${activity.description}</p>
                <p class="text-xs text-gray-500">${formatTimestamp(activity.timestamp)}</p>
            </div>
        </div>
    `).join('');

    feedDiv.innerHTML = activityHTML;
}

// Function to update active threats display
function updateActiveThreats() {
    fetch('/api/active-threats')
        .then(response => response.json())
        .then(data => {
            // Update count
            document.querySelector('#active-threats-count').textContent = data.count;
            
            // Update trend
            const trendEl = document.querySelector('#active-threats-trend');
            const trendIcon = data.trend < 0 ? '↓' : '↑';
            const trendClass = data.trend < 0 ? 'text-success' : 'text-danger';
            
            trendEl.innerHTML = `${trendIcon} ${Math.abs(data.trend)}% ${data.trend_direction} from last week`;
            trendEl.className = trendClass;
        })
        .catch(error => {
            console.error('Error fetching active threats:', error);
        });
}

// Update active threats every 30 seconds
setInterval(updateActiveThreats, 30000);

// Utility Functions
function getActivityIcon(type) {
    const icons = {
        'scan': 'fa-search',
        'threat': 'fa-shield-alt',
        'deepfake': 'fa-video',
        'alert': 'fa-exclamation-circle',
        'default': 'fa-info-circle'
    };
    return icons[type] || icons.default;
}

function formatTimestamp(timestamp) {
    return new Date(timestamp).toLocaleString();
}

function showNotification(message, type = 'info') {
    const notification = document.getElementById('notification');
    if (!notification) return;

    const classes = {
        'success': 'bg-green-500',
        'error': 'bg-red-500',
        'info': 'bg-blue-500',
        'warning': 'bg-yellow-500'
    };

    notification.className = `fixed top-4 right-4 p-4 rounded-lg text-white ${classes[type] || classes.info}`;
    notification.textContent = message;
    notification.style.display = 'block';

    setTimeout(() => {
        notification.style.display = 'none';
    }, 3000);
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadSecurityStatus();
    loadRecentActivity();
    updateActiveThreats();
    
    // Set up file drop zone
    const dropZone = document.getElementById('dropZone');
    if (dropZone) {
        dropZone.addEventListener('dragover', handleDragOver);
        dropZone.addEventListener('drop', handleDrop);
    }
});

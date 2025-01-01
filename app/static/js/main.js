// Utility function to show results
function showResult(elementId, data, isError = false) {
    const element = document.getElementById(elementId);
    element.innerHTML = '';
    
    if (isError) {
        element.innerHTML = `
            <div class="p-4 bg-red-100 text-red-700 rounded">
                ${data.error || 'An error occurred'}
            </div>
        `;
        return;
    }
    
    // Create result HTML based on data type
    let resultHTML = '';
    switch (elementId) {
        case 'urlScanResult':
            resultHTML = createUrlScanResult(data);
            break;
        case 'deepfakeResult':
            resultHTML = createDeepfakeResult(data);
            break;
        case 'spamResult':
            resultHTML = createSpamResult(data);
            break;
        default:
            resultHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    }
    
    element.innerHTML = resultHTML;
}

// Create URL scan result HTML
function createUrlScanResult(data) {
    const threatLevel = data.is_malicious ? 'High' : 'Low';
    const threatColor = data.is_malicious ? 'red' : 'green';
    
    return `
        <div class="p-4 bg-gray-50 rounded">
            <div class="flex justify-between items-center mb-2">
                <span class="font-semibold">Threat Level:</span>
                <span class="text-${threatColor}-600">${threatLevel}</span>
            </div>
            <div class="mb-2">
                <span class="font-semibold">Confidence:</span>
                <span>${(data.confidence * 100).toFixed(1)}%</span>
            </div>
            ${data.threats.length > 0 ? `
                <div class="mt-2">
                    <span class="font-semibold">Detected Threats:</span>
                    <ul class="list-disc pl-5 mt-1">
                        ${data.threats.map(threat => `<li>${threat}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

// Create deepfake detection result HTML
function createDeepfakeResult(data) {
    return `
        <div class="p-4 bg-gray-50 rounded">
            <div class="flex justify-between items-center mb-2">
                <span class="font-semibold">Result:</span>
                <span class="text-${data.is_fake ? 'red' : 'green'}-600">
                    ${data.is_fake ? 'Potential Deepfake' : 'Likely Authentic'}
                </span>
            </div>
            <div class="mb-2">
                <span class="font-semibold">Confidence:</span>
                <span>${(data.confidence * 100).toFixed(1)}%</span>
            </div>
            ${data.manipulated_regions?.length > 0 ? `
                <div class="mt-2">
                    <span class="font-semibold">Manipulated Regions:</span>
                    <ul class="list-disc pl-5 mt-1">
                        ${data.manipulated_regions.map(region => 
                            `<li>Region at (${region.x}, ${region.y})</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

// Create spam detection result HTML
function createSpamResult(data) {
    return `
        <div class="p-4 bg-gray-50 rounded">
            <div class="flex justify-between items-center mb-2">
                <span class="font-semibold">Result:</span>
                <span class="text-${data.is_spam ? 'red' : 'green'}-600">
                    ${data.is_spam ? 'Spam Detected' : 'Not Spam'}
                </span>
            </div>
            <div class="mb-2">
                <span class="font-semibold">Confidence:</span>
                <span>${(data.confidence * 100).toFixed(1)}%</span>
            </div>
            ${data.spam_type ? `
                <div class="mb-2">
                    <span class="font-semibold">Type:</span>
                    <span class="capitalize">${data.spam_type}</span>
                </div>
            ` : ''}
            ${data.detected_patterns?.length > 0 ? `
                <div class="mt-2">
                    <span class="font-semibold">Detected Patterns:</span>
                    <ul class="list-disc pl-5 mt-1">
                        ${data.detected_patterns.map(pattern => 
                            `<li>${pattern.type}: ${pattern.pattern}</li>`).join('')}
                    </ul>
                </div>
            ` : ''}
        </div>
    `;
}

// API call functions
async function scanUrl() {
    const url = document.getElementById('urlInput').value;
    if (!url) {
        showResult('urlScanResult', { error: 'Please enter a URL' }, true);
        return;
    }
    
    try {
        const response = await fetch('/api/scan-url', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url }),
        });
        
        const data = await response.json();
        showResult('urlScanResult', data);
    } catch (error) {
        showResult('urlScanResult', { error: error.message }, true);
    }
}

async function detectDeepfake() {
    const fileInput = document.getElementById('mediaInput');
    if (!fileInput.files.length) {
        showResult('deepfakeResult', { error: 'Please select a file' }, true);
        return;
    }
    
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    
    try {
        const response = await fetch('/api/detect-deepfake', {
            method: 'POST',
            body: formData,
        });
        
        const data = await response.json();
        showResult('deepfakeResult', data);
    } catch (error) {
        showResult('deepfakeResult', { error: error.message }, true);
    }
}

async function checkSpam() {
    const content = document.getElementById('contentInput').value;
    if (!content) {
        showResult('spamResult', { error: 'Please enter some content' }, true);
        return;
    }
    
    try {
        const response = await fetch('/api/check-spam', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ content }),
        });
        
        const data = await response.json();
        showResult('spamResult', data);
    } catch (error) {
        showResult('spamResult', { error: error.message }, true);
    }
}

async function reportThreat() {
    const title = document.getElementById('threatTitle').value;
    const description = document.getElementById('threatDescription').value;
    
    if (!title || !description) {
        alert('Please fill in both title and description');
        return;
    }
    
    try {
        const response = await fetch('/api/report-threat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ title, description }),
        });
        
        const data = await response.json();
        if (data.status === 'success') {
            alert('Threat report submitted successfully');
            document.getElementById('threatTitle').value = '';
            document.getElementById('threatDescription').value = '';
        }
    } catch (error) {
        alert('Error submitting threat report: ' + error.message);
    }
}

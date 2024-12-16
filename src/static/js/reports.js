// Reports Page JavaScript

// Filter reports based on type
function filterReports(type) {
    console.log('Filtering reports by type:', type);
    // Implement filtering logic here
}

// Filter reports based on date
function filterByDate(date) {
    console.log('Filtering reports by date:', date);
    // Implement date filtering logic here
}

// View report details
function viewReport(reportId) {
    const modal = document.getElementById('reportModal');
    modal.classList.add('active');
    
    // Fetch report details
    fetchReportDetails(reportId).then(details => {
        const modalBody = modal.querySelector('.modal-body');
        modalBody.innerHTML = generateReportHTML(details);
    });
}

// Download report
function downloadReport(reportId) {
    console.log('Downloading report:', reportId);
    // Implement download logic here
}

// Delete report
function deleteReport(reportId) {
    if (confirm('Are you sure you want to delete this report?')) {
        console.log('Deleting report:', reportId);
        // Implement delete logic here
    }
}

// Close modal
function closeModal() {
    const modal = document.getElementById('reportModal');
    modal.classList.remove('active');
}

// Pagination
function previousPage() {
    console.log('Loading previous page');
    // Implement previous page logic here
}

function nextPage() {
    console.log('Loading next page');
    // Implement next page logic here
}

// Export reports
function exportReports() {
    console.log('Exporting reports');
    // Implement export logic here
}

// Generate new report
function generateReport() {
    console.log('Generating new report');
    // Implement report generation logic here
}

// Fetch report details from server
async function fetchReportDetails(reportId) {
    // This is a mock implementation
    // Replace with actual API call
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({
                id: reportId,
                type: 'Scan Report',
                date: '2024-12-15 09:30',
                status: 'Completed',
                threats: 0,
                details: {
                    filesScanned: 1234,
                    scanDuration: '00:05:23',
                    threatTypes: [],
                    recommendations: []
                }
            });
        }, 500);
    });
}

// Generate HTML for report details
function generateReportHTML(report) {
    return `
        <div class="report-details">
            <div class="detail-group">
                <h3>Report Information</h3>
                <div class="detail-row">
                    <span class="detail-label">Report ID:</span>
                    <span class="detail-value">${report.id}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Type:</span>
                    <span class="detail-value">${report.type}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Date:</span>
                    <span class="detail-value">${report.date}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Status:</span>
                    <span class="detail-value">
                        <span class="status status-${report.status.toLowerCase()}">${report.status}</span>
                    </span>
                </div>
            </div>
            
            <div class="detail-group">
                <h3>Scan Details</h3>
                <div class="detail-row">
                    <span class="detail-label">Files Scanned:</span>
                    <span class="detail-value">${report.details.filesScanned}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Duration:</span>
                    <span class="detail-value">${report.details.scanDuration}</span>
                </div>
            </div>
            
            ${report.threats > 0 ? generateThreatsHTML(report.details.threatTypes) : ''}
            ${report.details.recommendations.length > 0 ? generateRecommendationsHTML(report.details.recommendations) : ''}
        </div>
    `;
}

// Generate HTML for threats section
function generateThreatsHTML(threats) {
    return `
        <div class="detail-group">
            <h3>Detected Threats</h3>
            <div class="threats-list">
                ${threats.map(threat => `
                    <div class="threat-item ${threat.severity.toLowerCase()}">
                        <div class="threat-header">
                            <span class="threat-name">${threat.name}</span>
                            <span class="threat-severity">${threat.severity}</span>
                        </div>
                        <p class="threat-description">${threat.description}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Generate HTML for recommendations section
function generateRecommendationsHTML(recommendations) {
    return `
        <div class="detail-group">
            <h3>Recommendations</h3>
            <div class="recommendations-list">
                ${recommendations.map(rec => `
                    <div class="recommendation-item">
                        <div class="recommendation-header">
                            <span class="recommendation-priority">${rec.priority}</span>
                            <span class="recommendation-title">${rec.title}</span>
                        </div>
                        <p class="recommendation-description">${rec.description}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Initialize page
document.addEventListener('DOMContentLoaded', function() {
    // Add any initialization code here
});

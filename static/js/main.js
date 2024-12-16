// Main JavaScript file for AI Defense System

// Initialize Bootstrap components
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize all popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Quick Actions Event Handlers
    setupQuickActions();
});

// Setup Quick Actions
function setupQuickActions() {
    // System Scan
    document.querySelector('.btn-primary')?.addEventListener('click', function() {
        showNotification('System scan initiated...', 'info');
        // Add your scan logic here
    });

    // Update Defense Rules
    document.querySelector('.btn-success')?.addEventListener('click', function() {
        showNotification('Updating defense rules...', 'info');
        // Add your update logic here
    });

    // Download Report
    document.querySelector('.btn-info')?.addEventListener('click', function() {
        showNotification('Generating report...', 'info');
        // Add your download logic here
    });

    // View Active Threats
    document.querySelector('.btn-warning')?.addEventListener('click', function() {
        window.location.href = '/threats/';
    });
}

// Show Notification
function showNotification(message, type = 'info') {
    const container = document.createElement('div');
    container.className = `alert alert-${type} alert-dismissible fade show notification-toast`;
    container.role = 'alert';
    
    container.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    document.body.appendChild(container);
    
    // Auto dismiss after 5 seconds
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(container);
        alert.close();
    }, 5000);
}

// Handle Settings Form Submission
document.addEventListener('submit', function(e) {
    if (e.target.matches('form')) {
        e.preventDefault();
        showNotification('Settings saved successfully!', 'success');
    }
});

// Update thread value display in settings
const threadRange = document.getElementById('max_threads');
if (threadRange) {
    const threadValue = document.getElementById('thread_value');
    threadRange.addEventListener('input', function() {
        threadValue.textContent = this.value;
    });
}

// Add animation class to threat cards when value changes
function updateThreatCount(element, newValue) {
    const oldValue = parseInt(element.textContent);
    element.textContent = newValue;
    
    if (newValue > oldValue) {
        element.classList.add('pulse-animation');
        setTimeout(() => {
            element.classList.remove('pulse-animation');
        }, 1000);
    }
}

// Dark mode toggle
function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    localStorage.setItem('darkMode', document.body.classList.contains('dark-mode'));
}

// Check for saved dark mode preference
if (localStorage.getItem('darkMode') === 'true') {
    document.body.classList.add('dark-mode');
}

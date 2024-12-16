// Handle alert dismissal
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
    });
});

// Handle form submissions with AJAX
document.addEventListener('submit', function(e) {
    const form = e.target;
    if (form.dataset.ajax) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {};
        formData.forEach((value, key) => data[key] = value);
        
        fetch(form.action, {
            method: form.method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                showAlert('success', data.message);
            } else if (data.error) {
                showAlert('danger', data.error);
            }
        })
        .catch(error => {
            showAlert('danger', 'An error occurred. Please try again.');
            console.error('Error:', error);
        });
    }
});

// Show alert function
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('main');
    container.insertBefore(alertDiv, container.firstChild);
    
    setTimeout(() => {
        alertDiv.style.opacity = '0';
        setTimeout(() => alertDiv.remove(), 300);
    }, 5000);
}

// Update active threats count
function updateActiveThreats() {
    fetch('/api/threats')
        .then(response => response.json())
        .then(data => {
            const threatCount = document.getElementById('active-threats-count');
            if (threatCount) {
                threatCount.textContent = data.length;
            }
        })
        .catch(error => console.error('Error:', error));
}

// Update dashboard stats periodically if on dashboard page
if (window.location.pathname === '/dashboard') {
    setInterval(updateActiveThreats, 30000); // Update every 30 seconds
}

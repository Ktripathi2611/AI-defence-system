document.addEventListener('DOMContentLoaded', function() {
    // System control buttons
    const startButton = document.getElementById('startSystem');
    const stopButton = document.getElementById('stopSystem');

    if (startButton) {
        startButton.addEventListener('click', function() {
            toggleSystem('start');
        });
    }

    if (stopButton) {
        stopButton.addEventListener('click', function() {
            toggleSystem('stop');
        });
    }

    function toggleSystem(action) {
        const url = `/api/system/${action}`;
        const button = action === 'start' ? startButton : stopButton;
        const otherButton = action === 'start' ? stopButton : startButton;

        // Disable both buttons during the request
        button.disabled = true;
        otherButton.disabled = true;

        // Add loading spinner
        const originalContent = button.innerHTML;
        button.innerHTML = `<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>Processing...`;

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            credentials: 'same-origin'
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                // Update system status badge
                const statusBadge = document.querySelector('.badge');
                if (statusBadge) {
                    statusBadge.className = `badge bg-${action === 'start' ? 'success' : 'danger'} p-2`;
                    statusBadge.innerHTML = `<i class="fas fa-circle me-1"></i>${action === 'start' ? 'Running' : 'Stopped'}`;
                }

                // Update button states
                button.disabled = true;
                otherButton.disabled = false;

                // Show success message
                showAlert('success', `System ${action === 'start' ? 'started' : 'stopped'} successfully`);
            } else {
                // Re-enable the clicked button on error
                button.disabled = false;
                otherButton.disabled = action === 'start';
                showAlert('danger', data.message || `Failed to ${action} system`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            button.disabled = false;
            otherButton.disabled = action === 'start';
            showAlert('danger', `Error ${action}ing system`);
        })
        .finally(() => {
            // Restore original button content
            button.innerHTML = originalContent;
        });
    }

    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed top-0 end-0 m-3`;
        alertDiv.style.zIndex = '1050';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.body.appendChild(alertDiv);

        // Remove the alert after 5 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    }
});

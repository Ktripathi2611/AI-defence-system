document.addEventListener('DOMContentLoaded', function() {
    // System control buttons
    const startButton = document.getElementById('startSystem');
    const stopButton = document.getElementById('stopSystem');
    const systemToast = document.getElementById('systemToast');
    const toastTitle = document.getElementById('toastTitle');
    const toastMessage = document.getElementById('toastMessage');
    
    // Bootstrap toast instance
    const toast = new bootstrap.Toast(systemToast);

    // Helper function to show toast notification
    function showToast(title, message, success = true) {
        toastTitle.textContent = title;
        toastMessage.textContent = message;
        systemToast.classList.remove('bg-success', 'bg-danger');
        systemToast.classList.add(success ? 'bg-success' : 'bg-danger');
        toast.show();
    }

    // Helper function to update button states
    function updateButtonStates(isRunning) {
        startButton.disabled = isRunning;
        stopButton.disabled = !isRunning;
    }

    // Helper function to handle system control
    async function handleSystemControl(action) {
        const button = action === 'start' ? startButton : stopButton;
        const originalContent = button.innerHTML;
        
        try {
            // Show loading state
            button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
            button.disabled = true;

            // Make API request
            const response = await fetch(`/api/system/${action}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            const data = await response.json();

            if (response.ok) {
                showToast('Success', data.message, true);
                // Update UI to reflect new state
                const statusBadge = document.querySelector('.badge');
                if (statusBadge) {
                    statusBadge.className = `badge bg-${action === 'start' ? 'success' : 'danger'} p-2`;
                    statusBadge.innerHTML = `<i class="fas fa-circle me-1"></i> ${action === 'start' ? 'Running' : 'Stopped'}`;
                }
                updateButtonStates(action === 'start');
            } else {
                throw new Error(data.message || 'Failed to control system');
            }
        } catch (error) {
            showToast('Error', error.message, false);
        } finally {
            // Restore button state
            button.innerHTML = originalContent;
            button.disabled = false;
        }
    }

    // Event listeners for system control buttons
    if (startButton) {
        startButton.addEventListener('click', () => handleSystemControl('start'));
    }
    if (stopButton) {
        stopButton.addEventListener('click', () => handleSystemControl('stop'));
    }

    // Update system stats periodically
    function updateSystemStats() {
        fetch('/api/system/stats')
            .then(response => response.json())
            .then(data => {
                // Update CPU usage
                const cpuElement = document.querySelector('[data-stat="cpu"]');
                if (cpuElement) {
                    const percentage = data.cpu_usage;
                    cpuElement.style.width = `${percentage}%`;
                    cpuElement.classList.toggle('bg-danger', percentage > 80);
                    cpuElement.classList.toggle('bg-success', percentage <= 80);
                }

                // Update memory usage
                const memoryElement = document.querySelector('[data-stat="memory"]');
                if (memoryElement) {
                    const percentage = data.memory_usage;
                    memoryElement.style.width = `${percentage}%`;
                    memoryElement.classList.toggle('bg-danger', percentage > 80);
                    memoryElement.classList.toggle('bg-success', percentage <= 80);
                }

                // Update other stats
                Object.entries(data).forEach(([key, value]) => {
                    const element = document.querySelector(`[data-stat="${key}"]`);
                    if (element) {
                        element.textContent = value;
                    }
                });
            })
            .catch(error => console.error('Failed to update system stats:', error));
    }

    // Update stats every 5 seconds
    setInterval(updateSystemStats, 5000);
});

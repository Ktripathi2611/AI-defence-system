// System Performance Monitor
let systemStats = {
    redis: { status: 'offline' },
    celery: { status: 'offline' },
    websocket: { status: 'disconnected' },
    cpu: 0,
    memory: 0,
    activeTasks: 0,
    events: []
};

// WebSocket connection for system updates
const systemSocket = new WebSocket(
    'ws://' + window.location.host + '/ws/tasks/'
);

function updateSystemStatus() {
    // Update status badges
    document.getElementById('redisStatus').innerHTML = `
        <span class="badge badge-${systemStats.redis.status === 'online' ? 'success' : 'danger'}">
            ${systemStats.redis.status === 'online' ? 'Online' : 'Offline'}
        </span>
    `;
    
    document.getElementById('celeryWorkerStatus').innerHTML = `
        <span class="badge badge-${systemStats.celery.status === 'online' ? 'success' : 'danger'}">
            ${systemStats.celery.status === 'online' ? 'Online' : 'Offline'}
        </span>
    `;
    
    document.getElementById('websocketStatus').innerHTML = `
        <span class="badge badge-${systemStats.websocket.status === 'connected' ? 'success' : 'danger'}">
            ${systemStats.websocket.status === 'connected' ? 'Connected' : 'Disconnected'}
        </span>
    `;

    // Update performance metrics
    document.getElementById('cpuUsage').textContent = `${systemStats.cpu}%`;
    document.getElementById('memoryUsage').textContent = `${systemStats.memory}%`;
    document.getElementById('activeTaskCount').textContent = systemStats.activeTasks;

    // Update event log
    updateEventLog();
}

function updateEventLog() {
    const tbody = document.getElementById('eventLogTable').getElementsByTagName('tbody')[0];
    tbody.innerHTML = '';
    
    systemStats.events.slice(0, 10).forEach(event => {
        const row = tbody.insertRow();
        row.innerHTML = `
            <td>${event.timestamp}</td>
            <td>${event.type}</td>
            <td>${event.message}</td>
            <td><span class="badge badge-${event.status === 'success' ? 'success' : 'danger'}">${event.status}</span></td>
        `;
    });
}

function addEvent(type, message, status = 'success') {
    const event = {
        timestamp: new Date().toLocaleTimeString(),
        type: type,
        message: message,
        status: status
    };
    
    systemStats.events.unshift(event);
    systemStats.events = systemStats.events.slice(0, 100); // Keep last 100 events
    updateEventLog();
}

systemSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    
    if (data.type === 'system_update') {
        systemStats = {
            ...systemStats,
            ...data.stats
        };
        updateSystemStatus();
    }
    
    if (data.type === 'worker_status') {
        systemStats.celery.status = data.online ? 'online' : 'offline';
        addEvent('Worker Status', `Celery worker ${data.online ? 'connected' : 'disconnected'}`, data.online ? 'success' : 'warning');
        updateSystemStatus();
    }

    if (data.type === 'task_update') {
        systemStats.activeTasks = data.stats.active;
        if (data.task) {
            addEvent('Task', `${data.task.name} - ${data.task.status}`, data.task.status === 'SUCCESS' ? 'success' : 'danger');
        }
        updateSystemStatus();
    }
};

systemSocket.onopen = function(e) {
    systemStats.websocket.status = 'connected';
    addEvent('WebSocket', 'Connected to server');
    updateSystemStatus();
};

systemSocket.onclose = function(e) {
    systemStats.websocket.status = 'disconnected';
    systemStats.celery.status = 'offline';
    addEvent('WebSocket', 'Disconnected from server', 'warning');
    updateSystemStatus();
};

// Initialize monitoring on page load
document.addEventListener('DOMContentLoaded', function() {
    updateSystemStatus();
    updateServicesStatus();
});

// Service Control Functions
function controlService(service, action) {
    fetch(`/api/services/${service}/${action}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            addEvent('Service Control', `${service} ${action} successful`, 'success');
        } else {
            addEvent('Service Control', `${service} ${action} failed: ${data.message}`, 'danger');
        }
    })
    .catch(error => {
        addEvent('Service Control', `Error controlling ${service}: ${error}`, 'danger');
    });
}

// Get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Add event listeners for service control buttons
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.service-control').forEach(button => {
        button.addEventListener('click', function() {
            const service = this.dataset.service;
            const action = this.dataset.action;
            controlService(service, action);
        });
    });
});

function updateServicesStatus() {
    fetch('/api/services/status/')
        .then(response => response.json())
        .then(data => {
            Object.entries(data).forEach(([service, status]) => {
                const startBtn = document.querySelector(`.service-control[data-service="${service}"][data-action="start"]`);
                const stopBtn = document.querySelector(`.service-control[data-service="${service}"][data-action="stop"]`);
                
                if (status) {
                    startBtn.disabled = true;
                    stopBtn.disabled = false;
                } else {
                    startBtn.disabled = false;
                    stopBtn.disabled = true;
                }
            });
        })
        .catch(error => {
            console.error('Error updating service status:', error);
        });
}

setInterval(() => {
    updateSystemStatus();
    updateServicesStatus();
}, 5000);

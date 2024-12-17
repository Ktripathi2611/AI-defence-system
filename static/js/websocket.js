class WebSocketClient {
    constructor(path) {
        this.connect(path);
        this.callbacks = {};
    }

    connect(path) {
        const wsScheme = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const wsPath = `${wsScheme}://${window.location.host}/ws/${path}`;
        
        this.socket = new WebSocket(wsPath);
        
        this.socket.onopen = () => {
            console.log('WebSocket connected');
            this.requestUpdate();
        };
        
        this.socket.onclose = () => {
            console.log('WebSocket disconnected');
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.connect(path), 5000);
        };
        
        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (this.callbacks[data.type]) {
                this.callbacks[data.type](data.data);
            }
        };
    }

    on(eventType, callback) {
        this.callbacks[eventType] = callback;
    }

    send(data) {
        if (this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify(data));
        }
    }

    requestUpdate() {
        this.send({ type: 'request_update' });
    }
}

// Dashboard WebSocket
class DashboardSocket extends WebSocketClient {
    constructor() {
        super('dashboard/');
    }

    updateStats(stats) {
        document.getElementById('active-threats').textContent = stats.active_threats;
        document.getElementById('system-health').textContent = stats.system_health + '%';
        document.getElementById('active-models').textContent = stats.active_models;
        document.getElementById('alerts-today').textContent = stats.alerts_today;
    }
}

// Threats WebSocket
class ThreatSocket extends WebSocketClient {
    constructor() {
        super('threats/');
    }

    updateThreats(data) {
        const threatList = document.getElementById('threat-list');
        if (!threatList) return;

        threatList.innerHTML = '';
        data.threats.forEach(threat => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${threat.id}</td>
                <td>${threat.type}</td>
                <td>${threat.source}</td>
                <td>${threat.target}</td>
                <td><span class="badge bg-${this.getSeverityClass(threat.severity)}">${threat.severity}</span></td>
                <td><span class="badge bg-${this.getStatusClass(threat.status)}">${threat.status}</span></td>
                <td>${threat.detected}</td>
                <td>
                    <div class="progress">
                        <div class="progress-bar" role="progressbar" style="width: ${threat.progress}" 
                             aria-valuenow="${parseInt(threat.progress)}" aria-valuemin="0" aria-valuemax="100">
                            ${threat.progress}
                        </div>
                    </div>
                </td>
            `;
            threatList.appendChild(row);
        });
    }

    getSeverityClass(severity) {
        const classes = {
            'High': 'danger',
            'Medium': 'warning',
            'Low': 'info'
        };
        return classes[severity] || 'secondary';
    }

    getStatusClass(status) {
        const classes = {
            'Active': 'danger',
            'Investigating': 'warning',
            'Resolved': 'success'
        };
        return classes[status] || 'secondary';
    }
}

// Network Scan WebSocket
class NetworkScanSocket extends WebSocketClient {
    constructor() {
        super('network-scan/');
    }

    startScan(params = {}) {
        this.send({
            type: 'start_scan',
            data: params
        });
    }

    updateScanResults(data) {
        const resultsList = document.getElementById('scan-results');
        if (!resultsList) return;

        resultsList.innerHTML = '';
        data.scan_results.forEach(result => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${result.ip}</td>
                <td>${result.host}</td>
                <td><span class="badge bg-${result.status === 'Online' ? 'success' : 'danger'}">${result.status}</span></td>
                <td>${result.open_ports}</td>
                <td>${result.services}</td>
                <td>${result.os}</td>
                <td><span class="badge bg-${this.getRiskClass(result.risk_level)}">${result.risk_level}</span></td>
            `;
            resultsList.appendChild(row);
        });
    }

    getRiskClass(risk) {
        const classes = {
            'High': 'danger',
            'Medium': 'warning',
            'Low': 'success'
        };
        return classes[risk] || 'secondary';
    }
}

// Redis WebSocket
class RedisSocket extends WebSocketClient {
    constructor() {
        super('redis/');
        this.setupEventListeners();
        this.retryCount = 0;
        this.maxRetries = 3;
    }

    setupEventListeners() {
        this.on('redis_stats', (data) => this.updateStats(data));
        this.on('redis_status', (data) => this.updateStatus(data.status, data.message));
    }

    updateStats(data) {
        if (!data) return;
        
        // Update basic stats with animation
        this.animateValue('redis-memory', data.memory);
        this.animateValue('redis-clients', data.clients);
        this.animateValue('redis-peak-clients', `Peak: ${data.peak_clients}`);
        this.animateValue('redis-ops', data.ops_per_sec);
        this.animateValue('redis-uptime', data.uptime);
    }

    animateValue(elementId, newValue) {
        const element = document.getElementById(elementId);
        if (!element) return;

        // Add fade effect
        element.style.opacity = '0.5';
        element.textContent = newValue;
        setTimeout(() => {
            element.style.opacity = '1';
        }, 100);
    }

    updateStatus(status, message = '') {
        const statusBadge = document.getElementById('redis-status');
        const startBtn = document.getElementById('start-redis');
        const stopBtn = document.getElementById('stop-redis');

        if (!statusBadge || !startBtn || !stopBtn) {
            console.error('Redis control elements not found');
            return;
        }

        switch (status) {
            case 'connected':
                statusBadge.className = 'badge bg-success ms-2';
                statusBadge.textContent = 'Connected';
                startBtn.disabled = true;
                stopBtn.disabled = false;
                this.retryCount = 0;
                if (message) showToast('Redis Connected', message, 'success');
                break;
            case 'disconnected':
                statusBadge.className = 'badge bg-danger ms-2';
                statusBadge.textContent = 'Disconnected';
                startBtn.disabled = false;
                stopBtn.disabled = true;
                if (message) showToast('Redis Disconnected', message, 'info');
                // Reset stats
                this.updateStats({
                    memory: '0 B',
                    clients: 0,
                    peak_clients: 0,
                    ops_per_sec: 0,
                    uptime: '0d 0h 0m'
                });
                break;
            case 'error':
                statusBadge.className = 'badge bg-warning ms-2';
                statusBadge.textContent = 'Error';
                startBtn.disabled = this.retryCount >= this.maxRetries;
                stopBtn.disabled = true;
                if (message) {
                    showToast('Redis Error', message, 'error');
                    console.error('Redis error:', message);
                }
                this.retryCount++;
                break;
            default:
                console.error('Unknown Redis status:', status);
        }
    }

    controlRedis(action) {
        if (action === 'start') {
            this.retryCount = 0;
        }
        console.log('Sending Redis control action:', action);
        this.send({
            type: 'control',
            action: action
        });
    }
}

// System Stats WebSocket
class SystemStatsSocket extends WebSocketClient {
    constructor() {
        super('system/');
        this.setupEventListeners();
    }

    setupEventListeners() {
        this.on('system_stats', (data) => this.updateSystemStats(data));
        this.on('performance_metrics', (data) => this.updatePerformanceMetrics(data));
    }

    updateSystemStats(data) {
        if (!data) return;

        // Update progress bars with animation
        this.animateProgressBar('cpu-usage-bar', 'cpu-usage-text', data.cpu_percent);
        this.animateProgressBar('memory-usage-bar', 'memory-usage-text', data.memory_percent);
        this.animateProgressBar('disk-usage-bar', 'disk-usage-text', data.disk_percent);

        // Update system health status
        const healthStatus = document.getElementById('system-health-status');
        if (data.cpu_percent > 90 || data.memory_percent > 90 || data.disk_percent > 90) {
            healthStatus.className = 'badge bg-danger';
            healthStatus.textContent = 'Critical';
        } else if (data.cpu_percent > 70 || data.memory_percent > 70 || data.disk_percent > 70) {
            healthStatus.className = 'badge bg-warning';
            healthStatus.textContent = 'Warning';
        } else {
            healthStatus.className = 'badge bg-success';
            healthStatus.textContent = 'Healthy';
        }
    }

    updatePerformanceMetrics(data) {
        if (!data) return;

        // Update performance metrics with animation
        this.animateValue('perf-cpu-usage', data.cpu_usage + '%');
        this.animateValue('perf-memory-usage', data.memory_usage + '%');
        this.animateValue('perf-active-tasks', data.active_tasks);
    }

    animateProgressBar(barId, textId, value) {
        const bar = document.getElementById(barId);
        const text = document.getElementById(textId);
        if (!bar || !text) return;

        // Update progress bar with smooth transition
        bar.style.transition = 'width 0.5s ease-in-out';
        bar.style.width = value + '%';
        bar.setAttribute('aria-valuenow', value);

        // Update text with fade effect
        text.style.opacity = '0.5';
        text.textContent = value + '%';
        setTimeout(() => {
            text.style.opacity = '1';
        }, 100);

        // Update progress bar color based on value
        if (value > 90) {
            bar.className = 'progress-bar bg-danger';
        } else if (value > 70) {
            bar.className = 'progress-bar bg-warning';
        } else {
            bar.className = 'progress-bar bg-primary';
        }
    }

    animateValue(elementId, newValue) {
        const element = document.getElementById(elementId);
        if (!element) return;

        element.style.transition = 'opacity 0.2s ease-in-out';
        element.style.opacity = '0.5';
        element.textContent = newValue;
        setTimeout(() => {
            element.style.opacity = '1';
        }, 100);
    }
}

// System Status Manager
class SystemStatusManager {
    constructor() {
        this.redisStatus = document.getElementById('redis-server-status');
        this.celeryStatus = document.getElementById('celery-worker-status');
        this.wsStatus = document.getElementById('websocket-status');
        this.checkInterval = null;
        this.startChecking();
    }

    startChecking() {
        // Initial check
        this.checkStatus();
        // Check every 30 seconds
        this.checkInterval = setInterval(() => this.checkStatus(), 30000);
    }

    updateStatus(element, status, message = '') {
        if (!element) return;
        
        switch (status) {
            case 'online':
                element.className = 'badge bg-success';
                element.textContent = 'Online';
                break;
            case 'offline':
                element.className = 'badge bg-danger';
                element.textContent = 'Offline';
                if (message) showToast('Service Offline', message, 'error');
                break;
            case 'error':
                element.className = 'badge bg-warning';
                element.textContent = 'Error';
                if (message) showToast('Service Error', message, 'warning');
                break;
            default:
                element.className = 'badge bg-secondary';
                element.textContent = 'Unknown';
        }
    }

    checkStatus() {
        // Check Redis status
        fetch('/api/status/redis')
            .then(response => response.json())
            .then(data => this.updateStatus(this.redisStatus, data.status, data.message))
            .catch(() => this.updateStatus(this.redisStatus, 'error'));

        // Check Celery status
        fetch('/api/status/celery')
            .then(response => response.json())
            .then(data => this.updateStatus(this.celeryStatus, data.status, data.message))
            .catch(() => this.updateStatus(this.celeryStatus, 'error'));

        // Update WebSocket status based on connection
        this.updateStatus(this.wsStatus, websocket.isConnected() ? 'online' : 'offline');
    }
}

// Initialize system status manager
const systemStatus = new SystemStatusManager();

// Initialize system stats socket
const systemStats = new SystemStatsSocket();

// Toast notification function
function showToast(title, message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) return;

    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');

    const bgClass = type === 'error' ? 'bg-danger text-white' : 
                   type === 'success' ? 'bg-success text-white' : 
                   'bg-light';

    toast.innerHTML = `
        <div class="toast-header ${bgClass}">
            <strong class="me-auto">${title}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="toast"></button>
        </div>
        <div class="toast-body">
            ${message}
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remove the toast after it's hidden
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

// Initialize Redis WebSocket
const redisSocket = new RedisSocket();

// Redis control function
function controlRedis(action) {
    console.log('Redis control action:', action);
    redisSocket.controlRedis(action);
}

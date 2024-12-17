class RedisMonitor {
    constructor() {
        this.socket = new WebSocket(`${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.host}/ws/redis-monitor/`);
        this.setupWebSocket();
        this.setupCharts();
    }

    setupWebSocket() {
        this.socket.onopen = () => {
            console.log('Redis monitor WebSocket connected');
            this.requestUpdate();
        };

        this.socket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.updateMetrics(data);
        };

        this.socket.onclose = () => {
            console.log('Redis monitor WebSocket disconnected');
            document.getElementById('redis-status').className = 'badge bg-danger ms-2';
            document.getElementById('redis-status').textContent = 'Disconnected';
            // Attempt to reconnect after 5 seconds
            setTimeout(() => this.connect(), 5000);
        };
    }

    setupCharts() {
        // Initialize ops/sec chart
        this.opsChart = new Chart(document.getElementById('redis-ops-chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Operations/sec',
                    data: [],
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    requestUpdate() {
        this.socket.send(JSON.stringify({
            type: 'request_update'
        }));
    }

    updateMetrics(data) {
        // Update status
        document.getElementById('redis-status').className = 'badge bg-success ms-2';
        document.getElementById('redis-status').textContent = 'Connected';

        // Update memory usage
        const memoryMB = (data.used_memory / 1024 / 1024).toFixed(2);
        document.getElementById('redis-memory').textContent = memoryMB;
        const memoryPercent = (data.used_memory / data.total_system_memory * 100).toFixed(1);
        document.getElementById('redis-memory-bar').style.width = `${memoryPercent}%`;

        // Update connected clients
        document.getElementById('redis-clients').textContent = data.connected_clients;
        document.getElementById('redis-peak-clients').textContent = `Peak: ${data.connected_clients_peak}`;

        // Update operations/sec
        document.getElementById('redis-ops').textContent = data.instantaneous_ops_per_sec;
        this.updateOpsChart(data.instantaneous_ops_per_sec);

        // Update uptime
        const uptimeDays = (data.uptime_in_seconds / 86400).toFixed(1);
        document.getElementById('redis-uptime').textContent = uptimeDays;
        if (data.last_save_time) {
            const lastSave = new Date(data.last_save_time * 1000).toLocaleString();
            document.getElementById('redis-last-save').textContent = `Last save: ${lastSave}`;
        }

        // Update command statistics
        const commandsTable = document.getElementById('redis-commands');
        commandsTable.innerHTML = '';
        Object.entries(data.commandstats).forEach(([cmd, stats]) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${cmd.replace('cmdstat_', '')}</td>
                <td>${stats.calls}</td>
                <td>${stats.usec_per_call.toFixed(2)}µs</td>
            `;
            commandsTable.appendChild(row);
        });

        // Update keyspace statistics
        const keyspaceTable = document.getElementById('redis-keyspace');
        keyspaceTable.innerHTML = '';
        Object.entries(data.keyspace).forEach(([db, stats]) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${db}</td>
                <td>${stats.keys}</td>
                <td>${stats.expires}</td>
                <td>${stats.avg_ttl}</td>
            `;
            keyspaceTable.appendChild(row);
        });
    }

    updateOpsChart(ops) {
        const now = new Date();
        const label = now.toLocaleTimeString();
        
        this.opsChart.data.labels.push(label);
        this.opsChart.data.datasets[0].data.push(ops);

        // Keep only last 20 data points
        if (this.opsChart.data.labels.length > 20) {
            this.opsChart.data.labels.shift();
            this.opsChart.data.datasets[0].data.shift();
        }

        this.opsChart.update();
    }
}

// Initialize Redis monitor when document is ready
document.addEventListener('DOMContentLoaded', () => {
    window.redisMonitor = new RedisMonitor();
});

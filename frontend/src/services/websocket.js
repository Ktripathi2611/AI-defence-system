class WebSocketService {
  constructor() {
    this.subscribers = new Set();
    this.mockInterval = null;
    this.threatCounter = 0;
    this.activeThreats = new Set();
    this.recentThreats = [];
  }

  generateThreat(currentTime) {
    const threatTypes = [
      {
        type: 'Phishing Attempt',
        severity: 'High',
        description: 'Blocked suspicious email',
        details: {
          source: `spam${Math.floor(Math.random() * 1000)}@malicious.com`,
          target: `user${Math.floor(Math.random() * 100)}@company.com`,
          technique: 'Credential Harvesting',
          action: 'Quarantined'
        }
      },
      {
        type: 'Malware',
        severity: 'Critical',
        description: 'Prevented file execution',
        details: {
          fileName: `malware${Math.floor(Math.random() * 100)}.exe`,
          hash: Array(32).fill(0).map(() => Math.floor(Math.random() * 16).toString(16)).join(''),
          type: 'Trojan',
          action: 'Deleted'
        }
      },
      {
        type: 'Network Intrusion',
        severity: 'Medium',
        description: 'Blocked suspicious connection',
        details: {
          source: `${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}.${Math.floor(Math.random() * 255)}`,
          port: Math.floor(Math.random() * 65535),
          protocol: 'TCP',
          action: 'Blocked'
        }
      }
    ];

    const threat = {
      ...threatTypes[Math.floor(Math.random() * threatTypes.length)],
      id: this.threatCounter++,
      timestamp: currentTime.toISOString()
    };

    // 30% chance the threat becomes active
    if (Math.random() < 0.3) {
      this.activeThreats.add(threat.id);
    }

    return threat;
  }

  updateThreats(currentTime) {
    // Add new threats (1-3 threats per update)
    const newThreatsCount = Math.floor(Math.random() * 3) + 1;
    for (let i = 0; i < newThreatsCount; i++) {
      const newThreat = this.generateThreat(currentTime);
      this.recentThreats.unshift(newThreat);
    }

    // Keep only last 24 hours of threats
    const twentyFourHoursAgo = new Date(currentTime - 24 * 60 * 60 * 1000);
    this.recentThreats = this.recentThreats.filter(threat => 
      new Date(threat.timestamp) > twentyFourHoursAgo
    );

    // Randomly resolve some active threats
    this.activeThreats.forEach(threatId => {
      if (Math.random() < 0.2) { // 20% chance to resolve each active threat
        this.activeThreats.delete(threatId);
      }
    });

    return {
      recentThreats: this.recentThreats.slice(0, 10), // Show only 10 most recent
      activeThreatsCount: this.activeThreats.size,
      totalThreats: this.recentThreats.length
    };
  }

  calculateProtectionScore() {
    const maxThreats = 100; // Baseline for 24 hours
    const activeThreatsWeight = 0.4;
    const totalThreatsWeight = 0.6;

    const activeThreatsScore = Math.max(0, 100 - (this.activeThreats.size * 5));
    const totalThreatsScore = Math.max(0, 100 - (this.recentThreats.length / maxThreats * 100));

    return Math.round(
      activeThreatsScore * activeThreatsWeight + 
      totalThreatsScore * totalThreatsWeight
    );
  }

  connect() {
    if (this.mockInterval) return;

    console.log('Starting mock WebSocket service');
    this.mockInterval = setInterval(() => {
      const currentTime = new Date();
      const { recentThreats, activeThreatsCount, totalThreats } = this.updateThreats(currentTime);

      const mockData = {
        type: 'metrics',
        data: {
          threatsBlocked: totalThreats,
          activeThreats: activeThreatsCount,
          protectionScore: this.calculateProtectionScore(),
          systemStatus: [
            { 
              component: 'Firewall',
              status: activeThreatsCount > 5 ? 'warning' : 'healthy',
              message: activeThreatsCount > 5 ? 'High threat activity' : 'Operating normally',
              details: {
                activeRules: Math.floor(Math.random() * 100) + 200,
                blockedIPs: Math.floor(totalThreats * 0.3),
                lastUpdated: new Date(currentTime - 1000 * 60 * 30).toISOString()
              }
            },
            { 
              component: 'Antivirus',
              status: 'healthy',
              message: 'Up to date',
              details: {
                definitions: 'Version ' + Math.floor(Math.random() * 100) + '.3.1',
                scannedFiles: Math.floor(Math.random() * 1000) + 5000,
                lastScan: new Date(currentTime - 1000 * 60 * 60 * 2).toISOString()
              }
            },
            { 
              component: 'Network Monitor',
              status: this.activeThreats.size > 3 ? 'warning' : 'healthy',
              message: this.activeThreats.size > 3 ? 'Elevated threat level' : 'Normal activity',
              details: {
                bandwidth: Math.floor(Math.random() * 100) + ' Mbps',
                connections: Math.floor(Math.random() * 100) + 50,
                activeThreats: this.activeThreats.size
              }
            }
          ],
          recentThreats
        }
      };

      this.subscribers.forEach(callback => callback(mockData));
    }, 3000);

    setTimeout(() => {
      this.subscribers.forEach(callback => 
        callback({ type: 'connection', status: 'connected' })
      );
    }, 500);
  }

  subscribe(callback) {
    this.subscribers.add(callback);
    this.connect();
    return () => this.unsubscribe(callback);
  }

  unsubscribe(callback) {
    this.subscribers.delete(callback);
    if (this.subscribers.size === 0) {
      this.disconnect();
    }
  }

  disconnect() {
    if (this.mockInterval) {
      clearInterval(this.mockInterval);
      this.mockInterval = null;
      console.log('Mock WebSocket service stopped');
    }
  }

  sendMessage(message) {
    console.log('Mock message sent:', message);
  }
}

const websocketService = new WebSocketService();
export default websocketService;

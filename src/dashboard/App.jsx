import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import SystemOverview from './components/SystemOverview';
import ResourceMonitor from './components/ResourceMonitor';
import ThreatAnalytics from './components/ThreatAnalytics';
import AlertManager from './components/AlertManager';
import NetworkMonitor from './components/NetworkMonitor';
import PerformanceGauge from './components/PerformanceGauge';

const App = () => {
  const [socket, setSocket] = useState(null);
  const [metrics, setMetrics] = useState({
    cpu_usage: 0,
    threats: 0,
    health: 100,
    tasks: 0
  });
  
  const [resourceData, setResourceData] = useState({
    timestamps: [],
    cpu: [],
    memory: [],
    gpu: []
  });
  
  const [threatData, setThreatData] = useState({
    timestamps: [],
    malware: [],
    deepfake: [],
    phishing: []
  });
  
  const [networkData, setNetworkData] = useState({
    timestamps: [],
    incoming: [],
    outgoing: []
  });
  
  const [performanceData, setPerformanceData] = useState({
    performance: 0,
    threshold: 80,
    cpuScore: 0,
    memoryScore: 0,
    ioScore: 0,
    insights: []
  });
  
  const [alerts, setAlerts] = useState([]);

  useEffect(() => {
    const newSocket = io('http://localhost:8080');
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to server');
    });

    newSocket.on('metrics_update', (data) => {
      setMetrics(data);
      updateResourceData(data);
    });

    newSocket.on('threats_update', (data) => {
      updateThreatData(data);
    });

    newSocket.on('network_update', (data) => {
      updateNetworkData(data);
    });

    newSocket.on('performance_update', (data) => {
      setPerformanceData(data);
    });

    newSocket.on('alerts_update', (data) => {
      setAlerts(data);
    });

    return () => {
      newSocket.close();
    };
  }, []);

  const updateResourceData = (data) => {
    const now = new Date();
    setResourceData(prev => {
      const newData = {
        timestamps: [...prev.timestamps, now],
        cpu: [...prev.cpu, data.cpu_usage],
        memory: [...prev.memory, data.memory_usage],
        gpu: [...prev.gpu, data.gpu_usage]
      };

      // Keep only last 60 data points
      if (newData.timestamps.length > 60) {
        Object.keys(newData).forEach(key => {
          newData[key] = newData[key].slice(-60);
        });
      }

      return newData;
    });
  };

  const updateThreatData = (data) => {
    const now = new Date();
    setThreatData(prev => {
      const newData = {
        timestamps: [...prev.timestamps, now],
        malware: [...prev.malware, data.malware],
        deepfake: [...prev.deepfake, data.deepfake],
        phishing: [...prev.phishing, data.phishing]
      };

      if (newData.timestamps.length > 60) {
        Object.keys(newData).forEach(key => {
          newData[key] = newData[key].slice(-60);
        });
      }

      return newData;
    });
  };

  const updateNetworkData = (data) => {
    const now = new Date();
    setNetworkData(prev => {
      const newData = {
        timestamps: [...prev.timestamps, now],
        incoming: [...prev.incoming, data.bytes_recv],
        outgoing: [...prev.outgoing, data.bytes_sent]
      };

      if (newData.timestamps.length > 60) {
        Object.keys(newData).forEach(key => {
          newData[key] = newData[key].slice(-60);
        });
      }

      return newData;
    });
  };

  const handleAcknowledgeAlert = (alertId) => {
    socket.emit('acknowledge_alert', alertId);
  };

  const handleAcknowledgeAllAlerts = () => {
    socket.emit('acknowledge_all_alerts');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-lg">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-2xl font-bold text-gray-800">AI Defence System</h1>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <SystemOverview metrics={metrics} />
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-8">
          <ResourceMonitor data={resourceData} />
          <ThreatAnalytics data={threatData} />
          <NetworkMonitor data={networkData} />
          <PerformanceGauge data={performanceData} />
        </div>

        <AlertManager 
          alerts={alerts}
          onAcknowledge={handleAcknowledgeAlert}
          onAcknowledgeAll={handleAcknowledgeAllAlerts}
        />
      </main>
    </div>
  );
};

export default App;

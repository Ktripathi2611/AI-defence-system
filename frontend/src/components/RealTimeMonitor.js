import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Switch,
  List,
  ListItem,
  ListItemText,
  Alert,
  IconButton,
  Collapse,
  Paper,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  VideoCall as VideoIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

function RealTimeMonitor() {
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [ws, setWs] = useState(null);

  const connectWebSocket = useCallback(() => {
    const websocket = new WebSocket('ws://localhost:8080/ws/monitor');

    websocket.onopen = () => {
      console.log('Connected to monitoring WebSocket');
    };

    websocket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'status') {
        setIsMonitoring(data.data.threat_monitoring);
      } else {
        setAlerts(prev => [{
          id: Date.now(),
          ...data
        }, ...prev].slice(0, 10)); // Keep only last 10 alerts
      }
    };

    websocket.onclose = () => {
      console.log('Monitor WebSocket disconnected. Attempting to reconnect...');
      setTimeout(connectWebSocket, 3000);
    };

    setWs(websocket);
    return websocket;
  }, []);

  useEffect(() => {
    const websocket = connectWebSocket();
    return () => {
      websocket.close();
    };
  }, [connectWebSocket]);

  const handleMonitoringToggle = () => {
    if (ws && ws.readyState === WebSocket.OPEN) {
      const newState = !isMonitoring;
      ws.send(JSON.stringify({
        action: newState ? 'start_monitoring' : 'stop_monitoring'
      }));
      setIsMonitoring(newState);
    }
  };

  const removeAlert = (alertId) => {
    setAlerts(prev => prev.filter(alert => alert.id !== alertId));
  };

  const getAlertDetails = (alert) => {
    switch (alert.type) {
      case 'threat':
        return {
          icon: <SecurityIcon color="error" />,
          title: 'Threat Detected',
          severity: 'error',
          details: `Malicious URL detected: ${alert.data.url}`
        };
      case 'spam':
        return {
          icon: <WarningIcon color="warning" />,
          title: 'Spam Detected',
          severity: 'warning',
          details: `Spam message detected with score: ${alert.data.spam_score}`
        };
      case 'deepfake':
        return {
          icon: <VideoIcon color="error" />,
          title: 'Deepfake Detected',
          severity: 'error',
          details: `Deepfake detected with confidence: ${alert.data.deepfake_score}`
        };
      default:
        return {
          icon: <WarningIcon />,
          title: 'Alert',
          severity: 'info',
          details: 'Unknown alert type'
        };
    }
  };

  return (
    <Box sx={{ mb: 4 }}>
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Real-Time Monitoring
            </Typography>
            <Switch
              checked={isMonitoring}
              onChange={handleMonitoringToggle}
              color="primary"
            />
          </Box>
          
          <Paper elevation={0} sx={{ bgcolor: 'background.default', p: 2 }}>
            <Typography variant="subtitle2" color="text.secondary" gutterBottom>
              Active Monitoring:
            </Typography>
            <List dense>
              <ListItem>
                <ListItemText 
                  primary="URL Scanning"
                  secondary={isMonitoring ? "Active" : "Inactive"}
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Spam Detection"
                  secondary={isMonitoring ? "Active" : "Inactive"}
                />
              </ListItem>
              <ListItem>
                <ListItemText 
                  primary="Deepfake Detection"
                  secondary={isMonitoring ? "Active" : "Inactive"}
                />
              </ListItem>
            </List>
          </Paper>

          <Box sx={{ mt: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Recent Alerts
            </Typography>
            {alerts.map(alert => {
              const { icon, title, severity, details } = getAlertDetails(alert);
              return (
                <Collapse key={alert.id} in={true}>
                  <Alert
                    severity={severity}
                    icon={icon}
                    action={
                      <IconButton
                        aria-label="close"
                        color="inherit"
                        size="small"
                        onClick={() => removeAlert(alert.id)}
                      >
                        <CloseIcon fontSize="inherit" />
                      </IconButton>
                    }
                    sx={{ mb: 1 }}
                  >
                    <Typography variant="subtitle2">{title}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {details}
                    </Typography>
                  </Alert>
                </Collapse>
              );
            })}
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
}

export default RealTimeMonitor;

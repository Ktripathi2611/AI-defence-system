import React, { useState, useEffect, useCallback } from 'react';
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  CircularProgress,
  LinearProgress
} from '@mui/material';
import {
  Shield as ShieldIcon,
  Warning as WarningIcon,
  TrendingUp as TrendingUpIcon,
  Security as SecurityIcon,
  Error as ErrorIcon
} from '@mui/icons-material';
import websocketService from '../services/websocket';

const MetricCard = ({ icon, title, subtitle, value, color, loading }) => (
  <Card sx={{ 
    height: '100%', 
    bgcolor: 'rgba(0, 0, 0, 0.2)', 
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: 2,
    position: 'relative',
    minHeight: '180px'
  }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        {React.cloneElement(icon, { sx: { color: color, fontSize: 28, mr: 1 } })}
        <Box>
          <Typography variant="h6" color="white">
            {title}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {subtitle}
          </Typography>
        </Box>
      </Box>
      {loading ? (
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center',
          height: '100px'
        }}>
          <CircularProgress 
            size={40}
            sx={{ 
              color: color,
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              }
            }} 
          />
        </Box>
      ) : (
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <LinearProgress
            variant="determinate"
            value={value}
            sx={{
              height: 8,
              borderRadius: 4,
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              mb: 2,
              '& .MuiLinearProgress-bar': {
                backgroundColor: color,
                borderRadius: 4,
              },
            }}
          />
          <Typography variant="h2" color="white" sx={{ fontWeight: 'bold' }}>
            {value}
          </Typography>
        </Box>
      )}
    </CardContent>
  </Card>
);

const StatusSection = ({ title, icon, loading, children }) => (
  <Card sx={{ 
    height: '100%', 
    bgcolor: 'rgba(0, 0, 0, 0.2)', 
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: 2,
    position: 'relative',
    minHeight: '300px'
  }}>
    <CardContent>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        {React.cloneElement(icon, { sx: { fontSize: 24, mr: 1 } })}
        <Typography variant="h6" color="white">
          {title}
        </Typography>
      </Box>
      {loading ? (
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          alignItems: 'center',
          height: '200px'
        }}>
          <CircularProgress 
            size={40}
            sx={{ 
              color: '#2196f3',
              '& .MuiCircularProgress-circle': {
                strokeLinecap: 'round',
              }
            }} 
          />
        </Box>
      ) : (
        children
      )}
    </CardContent>
  </Card>
);

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [data, setData] = useState({
    threatsBlocked: 0,
    activeThreats: 0,
    protectionScore: 0,
    systemStatus: [],
    recentThreats: []
  });

  const handleWebSocketMessage = useCallback((message) => {
    if (message.type === 'metrics') {
      setData(prevData => ({
        ...prevData,
        ...message.data
      }));
      setLoading(false);
    }
  }, []);

  const fetchInitialData = useCallback(async () => {
    try {
      setLoading(true);
      // Use mock data for initial load
      const mockData = {
        threatsBlocked: Math.floor(Math.random() * 100),
        activeThreats: Math.floor(Math.random() * 20),
        protectionScore: Math.floor(Math.random() * (100 - 70) + 70),
        systemStatus: [
          { 
            component: 'Firewall', 
            status: 'healthy', 
            message: 'Operating normally', 
            details: {
              'Uptime': '24 hours',
              'Memory Usage': '50%',
              'CPU Usage': '20%'
            } 
          },
          { 
            component: 'Antivirus', 
            status: 'healthy', 
            message: 'Up to date', 
            details: {
              'Last Scan': '1 hour ago',
              'Virus Definitions': 'Updated',
              'Threats Detected': '0'
            } 
          },
          { 
            component: 'Network Monitor', 
            status: 'warning', 
            message: 'High traffic detected', 
            details: {
              'Traffic Volume': '1000 MB/s',
              'Packet Loss': '5%',
              'Latency': '50 ms'
            } 
          }
        ],
        recentThreats: [
          { 
            type: 'Phishing Attempt', 
            description: 'Blocked suspicious email', 
            timestamp: new Date().toISOString(), 
            severity: 'High', 
            details: {
              'Source IP': '192.168.1.100',
              'Destination IP': '192.168.1.200',
              'Protocol': 'TCP'
            } 
          },
          { 
            type: 'Malware', 
            description: 'Prevented file execution', 
            timestamp: new Date().toISOString(), 
            severity: 'Critical', 
            details: {
              'File Name': 'malware.exe',
              'File Hash': 'abc123',
              'Detection Method': 'Signature-based'
            } 
          }
        ]
      };
      setData(mockData);
    } catch (error) {
      console.error('Failed to fetch initial data:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInitialData();
    const unsubscribe = websocketService.subscribe(handleWebSocketMessage);
    return () => unsubscribe();
  }, [fetchInitialData, handleWebSocketMessage]);

  const getStatusIcon = useCallback((status) => {
    switch (status) {
      case 'healthy':
        return <SecurityIcon sx={{ color: '#4caf50' }} />;
      case 'warning':
        return <WarningIcon sx={{ color: '#ff9800' }} />;
      default:
        return <ErrorIcon sx={{ color: '#f50057' }} />;
    }
  }, []);

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <MetricCard
            icon={<ShieldIcon />}
            title="Threats Blocked"
            subtitle="Total threats prevented in last 24 hours"
            value={data.threatsBlocked}
            color="#2196f3"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <MetricCard
            icon={<WarningIcon />}
            title="Active Threats"
            subtitle="Current security alerts requiring attention"
            value={data.activeThreats}
            color="#f50057"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <MetricCard
            icon={<TrendingUpIcon />}
            title="Protection Score"
            subtitle="Overall system security rating"
            value={data.protectionScore}
            color="#4caf50"
            loading={loading}
          />
        </Grid>

        <Grid item xs={12} md={8}>
          <StatusSection 
            title="System Status" 
            icon={<SecurityIcon color="primary" />}
            loading={loading}
          >
            <Box sx={{ height: '300px', overflowY: 'auto' }}>
              {data.systemStatus.map((status, index) => (
                <Box 
                  key={index}
                  sx={{ 
                    p: 2, 
                    mb: 1, 
                    bgcolor: 'rgba(32, 33, 35, 0.5)',
                    borderRadius: 1,
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: 2
                  }}
                >
                  {getStatusIcon(status.status)}
                  <Box sx={{ flex: 1 }}>
                    <Typography color="white" variant="subtitle1">
                      {status.component}
                    </Typography>
                    <Typography color="text.secondary" variant="body2" sx={{ mb: 1 }}>
                      {status.message}
                    </Typography>
                    <Box sx={{ 
                      bgcolor: 'rgba(0, 0, 0, 0.2)', 
                      borderRadius: 1, 
                      p: 1.5,
                      fontSize: '0.875rem'
                    }}>
                      {Object.entries(status.details).map(([key, value]) => (
                        <Box key={key} sx={{ display: 'flex', mb: 0.5 }}>
                          <Typography 
                            color="rgba(255, 255, 255, 0.5)" 
                            sx={{ minWidth: 120 }}
                          >
                            {key.charAt(0).toUpperCase() + key.slice(1)}:
                          </Typography>
                          <Typography color="rgba(255, 255, 255, 0.8)">
                            {value}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </Box>
                </Box>
              ))}
            </Box>
          </StatusSection>
        </Grid>

        <Grid item xs={12} md={4}>
          <StatusSection 
            title="Recent Threats" 
            icon={<ErrorIcon sx={{ color: '#f50057' }} />}
            loading={loading}
          >
            <Box sx={{ height: '300px', overflowY: 'auto', pr: 1 }}>
              {data.recentThreats.map((threat, index) => (
                <Box 
                  key={index}
                  sx={{ 
                    p: 2.5,
                    mb: 1.5, 
                    bgcolor: 'rgba(32, 33, 35, 0.5)',
                    borderRadius: 1,
                    '&:hover': {
                      bgcolor: 'rgba(32, 33, 35, 0.7)',
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                    <Typography 
                      color="white" 
                      variant="subtitle1" 
                      sx={{ 
                        fontWeight: 500,
                        display: 'flex',
                        alignItems: 'center',
                        gap: 1
                      }}
                    >
                      {threat.type}
                      <Box
                        sx={{
                          px: 1,
                          py: 0.5,
                          borderRadius: 1,
                          fontSize: '0.75rem',
                          bgcolor: threat.severity === 'Critical' ? 'error.dark' : 
                                  threat.severity === 'High' ? 'warning.dark' : 'info.dark'
                        }}
                      >
                        {threat.severity}
                      </Box>
                    </Typography>
                  </Box>
                  <Typography 
                    color="rgba(255, 255, 255, 0.7)" 
                    variant="body2"
                    sx={{ mb: 1 }}
                  >
                    {threat.description}
                  </Typography>
                  <Box sx={{ 
                    bgcolor: 'rgba(0, 0, 0, 0.2)', 
                    borderRadius: 1, 
                    p: 1.5, 
                    mb: 1.5,
                    fontSize: '0.875rem'
                  }}>
                    {Object.entries(threat.details).map(([key, value]) => (
                      <Box key={key} sx={{ display: 'flex', mb: 0.5 }}>
                        <Typography 
                          color="rgba(255, 255, 255, 0.5)" 
                          sx={{ minWidth: 100 }}
                        >
                          {key.charAt(0).toUpperCase() + key.slice(1)}:
                        </Typography>
                        <Typography color="rgba(255, 255, 255, 0.8)">
                          {value}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                  <Typography 
                    color="rgba(255, 255, 255, 0.5)" 
                    variant="caption" 
                    sx={{ 
                      display: 'block',
                      fontSize: '0.75rem'
                    }}
                  >
                    {new Date(threat.timestamp).toLocaleString('en-US', {
                      month: 'numeric',
                      day: 'numeric',
                      year: 'numeric',
                      hour: 'numeric',
                      minute: 'numeric',
                      hour12: true
                    })}
                  </Typography>
                </Box>
              ))}
            </Box>
          </StatusSection>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Dashboard;

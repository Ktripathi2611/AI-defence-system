import React, { useState, useEffect, useCallback } from 'react';
import {
  Grid,
  Paper,
  Typography,
  Box,
  useTheme,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Warning as WarningIcon,
  School as SchoolIcon,
  Group as GroupIcon,
} from '@mui/icons-material';
import RealTimeMonitor from '../components/RealTimeMonitor';

function Dashboard() {
  const [stats, setStats] = useState({
    spam_detected: 0,
    threats_blocked: 0,
    deepfakes_identified: 0,
    community_reports: 0,
  });

  const theme = useTheme();

  const connectWebSocket = useCallback(() => {
    const ws = new WebSocket('ws://localhost:8080/ws');

    ws.onopen = () => {
      console.log('Connected to WebSocket');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setStats({
        spam_detected: data.spam_detected,
        threats_blocked: data.threats_blocked,
        deepfakes_identified: data.deepfakes_identified,
        community_reports: data.community_reports,
      });
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected. Attempting to reconnect...');
      setTimeout(connectWebSocket, 3000);
    };

    return ws;
  }, []);

  useEffect(() => {
    const ws = connectWebSocket();
    return () => {
      ws.close();
    };
  }, [connectWebSocket]);

  const cards = [
    {
      title: 'Spam Detected',
      value: stats.spam_detected,
      icon: <SecurityIcon sx={{ fontSize: 40, color: theme.palette.primary.main }} />,
      color: theme.palette.primary.light,
    },
    {
      title: 'Threats Blocked',
      value: stats.threats_blocked,
      icon: <WarningIcon sx={{ fontSize: 40, color: theme.palette.error.main }} />,
      color: theme.palette.error.light,
    },
    {
      title: 'Deepfakes Identified',
      value: stats.deepfakes_identified,
      icon: <SchoolIcon sx={{ fontSize: 40, color: theme.palette.success.main }} />,
      color: theme.palette.success.light,
    },
    {
      title: 'Community Reports',
      value: stats.community_reports,
      icon: <GroupIcon sx={{ fontSize: 40, color: theme.palette.warning.main }} />,
      color: theme.palette.warning.light,
    },
  ];

  return (
    <Box sx={{ flexGrow: 1 }}>
      <Typography variant="h4" gutterBottom sx={{ mb: 4 }}>
        Dashboard
      </Typography>
      
      {/* Real-time Monitor */}
      <RealTimeMonitor />
      
      {/* Stats Cards */}
      <Grid container spacing={3}>
        {cards.map((card) => (
          <Grid item xs={12} sm={6} md={3} key={card.title}>
            <Paper
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                backgroundColor: card.color,
                borderRadius: 2,
                transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
              }}
            >
              {card.icon}
              <Typography variant="h4" component="div" sx={{ mt: 2, fontWeight: 'bold' }}>
                {card.value}
              </Typography>
              <Typography variant="subtitle1" color="text.secondary" sx={{ mt: 1 }}>
                {card.title}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default Dashboard;

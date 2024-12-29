import React, { useState, useEffect } from 'react';
import { 
  Container, 
  Grid, 
  Card, 
  CardContent, 
  Typography, 
  Box,
  List,
  ListItem,
  ListItemText,
  CircularProgress,
  Alert,
  Paper,
  Divider,
  Tooltip,
  IconButton,
  LinearProgress,
  Button
} from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import ShieldIcon from '@mui/icons-material/Shield';
import BugReportIcon from '@mui/icons-material/BugReport';
import TimelineIcon from '@mui/icons-material/Timeline';
import config from '../config';

const StatCard = ({ title, value, icon, color, loading, subtitle, progress }) => (
  <Card sx={{ 
    height: '100%', 
    position: 'relative',
    backgroundColor: 'rgba(0, 0, 0, 0.2)',
    backdropFilter: 'blur(10px)',
    border: '1px solid rgba(255, 255, 255, 0.1)'
  }}>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        {icon}
        <Box ml={1}>
          <Typography variant="h6" component="div" color="white">
            {title}
          </Typography>
          {subtitle && (
            <Typography variant="caption" color="grey.400">
              {subtitle}
            </Typography>
          )}
        </Box>
      </Box>
      <Typography variant="h3" component="div" color={color} sx={{ mb: 1 }}>
        {loading ? <CircularProgress size={30} /> : value}
      </Typography>
      {progress !== undefined && (
        <Box sx={{ width: '100%', mt: 2 }}>
          <LinearProgress 
            variant="determinate" 
            value={progress} 
            color={color}
            sx={{ 
              height: 8, 
              borderRadius: 4,
              backgroundColor: 'rgba(255, 255, 255, 0.1)',
              '& .MuiLinearProgress-bar': {
                borderRadius: 4
              }
            }}
          />
        </Box>
      )}
    </CardContent>
  </Card>
);

const DetailCard = ({ title, items, icon, loading }) => (
  <Paper sx={{ p: 2, height: '100%', backgroundColor: 'rgba(0, 0, 0, 0.2)' }}>
    <Box display="flex" alignItems="center" mb={2}>
      {icon}
      <Typography variant="h6" ml={1} color="white">
        {title}
      </Typography>
    </Box>
    {loading ? (
      <CircularProgress />
    ) : items && items.length > 0 ? (
      <List>
        {items.map((item, index) => (
          <React.Fragment key={index}>
            <ListItem>
              <ListItemText
                primary={
                  <Typography variant="subtitle1" color="white">
                    {item.title || item.type}
                  </Typography>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="grey.400">
                      {item.description}
                    </Typography>
                    <Typography variant="caption" color="grey.500">
                      Last updated: {new Date(item.timestamp).toLocaleString()}
                    </Typography>
                    {item.severity && (
                      <Box 
                        component="span" 
                        sx={{ 
                          ml: 1,
                          px: 1,
                          py: 0.5,
                          borderRadius: 1,
                          backgroundColor: 
                            item.severity === 'High' ? 'error.dark' :
                            item.severity === 'Medium' ? 'warning.dark' :
                            'success.dark',
                          color: 'white',
                          fontSize: '0.75rem'
                        }}
                      >
                        {item.severity}
                      </Box>
                    )}
                  </Box>
                }
              />
            </ListItem>
            {index < items.length - 1 && <Divider sx={{ borderColor: 'grey.800' }} />}
          </React.Fragment>
        ))}
      </List>
    ) : (
      <Typography color="grey.400">No data available</Typography>
    )}
  </Paper>
);

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchDashboardStats = async () => {
    try {
      const response = await fetch(`${config.API_URL}/dashboard/stats`);
      if (!response.ok) {
        throw new Error('Failed to fetch dashboard statistics');
      }
      const data = await response.json();
      setStats(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardStats();
    const interval = setInterval(fetchDashboardStats, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  // Function to simulate a new threat (for testing)
  const simulateThreat = async () => {
    try {
      await fetch(`${config.API_URL}/simulate/threat`, { method: 'POST' });
      fetchDashboardStats(); // Refresh stats after simulation
    } catch (err) {
      console.error('Error simulating threat:', err);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 3 }}
          action={
            <Tooltip title="Check your network connection and ensure the backend server is running">
              <IconButton color="inherit" size="small">
                <InfoIcon />
              </IconButton>
            </Tooltip>
          }
        >
          {error}
        </Alert>
      )}
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <StatCard
            title="Threats Blocked"
            subtitle="Total threats prevented in last 24 hours"
            value={stats?.threats_blocked || 0}
            icon={<ShieldIcon sx={{ color: '#2196f3', fontSize: 40 }} />}
            color="primary"
            loading={loading}
            progress={75}
          />
        </Grid>

        <Grid item xs={12} md={4}>
          <StatCard
            title="Active Threats"
            subtitle="Current security alerts requiring attention"
            value={stats?.active_threats || 0}
            icon={<BugReportIcon sx={{ color: '#f50057', fontSize: 40 }} />}
            color="error"
            loading={loading}
            progress={15}
          />
        </Grid>

        <Grid item xs={12} md={4}>
          <StatCard
            title="Protection Score"
            subtitle="Overall system security rating"
            value={stats ? `${stats.protection_score}%` : '100%'}
            icon={<TimelineIcon sx={{ color: '#4caf50', fontSize: 40 }} />}
            color="success"
            loading={loading}
            progress={stats?.protection_score || 100}
          />
        </Grid>
      </Grid>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={6}>
          <DetailCard
            title="System Status"
            items={stats?.system_status || []}
            icon={<SecurityIcon sx={{ color: '#2196f3' }} />}
            loading={loading}
          />
        </Grid>

        <Grid item xs={12} md={6}>
          <DetailCard
            title="Recent Threats"
            items={stats?.recent_threats || []}
            icon={<WarningIcon sx={{ color: '#f50057' }} />}
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* Debug button - only show in development */}
      {process.env.NODE_ENV === 'development' && (
        <Box sx={{ mt: 2 }}>
          <Button 
            variant="contained" 
            color="secondary" 
            onClick={simulateThreat}
            startIcon={<BugReportIcon />}
          >
            Simulate Threat
          </Button>
        </Box>
      )}
    </Container>
  );
};

export default Dashboard;

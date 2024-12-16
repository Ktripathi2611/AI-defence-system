import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Box,
} from '@mui/material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts';

const ThreatMetrics = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchMetrics();
    const interval = setInterval(fetchMetrics, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('/api/metrics/threats');
      const data = await response.json();
      setMetrics(data);
    } catch (error) {
      console.error('Error fetching threat metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="200px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Grid container spacing={3}>
      {/* Threat Summary Card */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Threat Summary
            </Typography>
            <Typography variant="h3" color="primary">
              {metrics?.totalThreats || 0}
            </Typography>
            <Typography variant="subtitle1" color="textSecondary">
              Total Threats Detected
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Threat Types Distribution */}
      <Grid item xs={12} md={8}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Threat Distribution
            </Typography>
            <LineChart
              width={600}
              height={300}
              data={metrics?.threatDistribution || []}
              margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="malware"
                stroke="#8884d8"
                name="Malware"
              />
              <Line
                type="monotone"
                dataKey="deepfake"
                stroke="#82ca9d"
                name="Deepfake"
              />
              <Line
                type="monotone"
                dataKey="phishing"
                stroke="#ffc658"
                name="Phishing"
              />
            </LineChart>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default ThreatMetrics;

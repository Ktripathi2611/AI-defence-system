import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import { BugReport as BugReportIcon, Security as SecurityIcon } from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function ThreatAnalysis() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async () => {
    if (!url) {
      setError('Please enter a URL to analyze');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/threats/analyze/url`, {
        url: url
      });
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while analyzing the URL');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Threat Analysis
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Analyze URL for Threats
          </Typography>
          
          <TextField
            fullWidth
            label="Enter URL"
            variant="outlined"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            sx={{ mb: 2 }}
          />
          
          <Button
            variant="contained"
            color="primary"
            onClick={handleAnalyze}
            disabled={loading}
            startIcon={<BugReportIcon />}
          >
            Analyze URL
          </Button>

          {loading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
              <CircularProgress />
            </Box>
          )}

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          {result && (
            <Box sx={{ mt: 2 }}>
              <Alert
                severity={result.threat_level === 'high' ? 'error' : result.threat_level === 'medium' ? 'warning' : 'success'}
                icon={<SecurityIcon />}
              >
                Threat Level: {result.threat_level.toUpperCase()}
              </Alert>

              <Typography variant="h6" sx={{ mt: 2 }}>
                Analysis Details
              </Typography>
              <List>
                {result.threats?.map((threat, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <BugReportIcon color={threat.severity === 'high' ? 'error' : 'warning'} />
                    </ListItemIcon>
                    <ListItemText
                      primary={threat.type}
                      secondary={threat.description}
                    />
                  </ListItem>
                ))}
              </List>

              <Typography variant="h6" sx={{ mt: 2 }}>
                Safety Recommendations
              </Typography>
              <List>
                {result.recommendations?.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <SecurityIcon color="info" />
                    </ListItemIcon>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default ThreatAnalysis;

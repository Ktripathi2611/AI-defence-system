import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Security,
  Warning,
  CheckCircle,
  Error as ErrorIcon,
} from '@mui/icons-material';

const ThreatLevelChip = ({ level }) => {
  const getColor = () => {
    if (level < 30) return 'success';
    if (level < 70) return 'warning';
    return 'error';
  };

  return (
    <Chip
      label={`Threat Level: ${level}%`}
      color={getColor()}
      icon={<Security />}
      sx={{ ml: 1 }}
    />
  );
};

const ScanResults = ({ results }) => {
  const {
    filename,
    timestamp,
    threat_level,
    deepfake_detection,
    malware_analysis,
    overall_status,
    threats_found,
  } = results;

  return (
    <Grid container spacing={3}>
      {/* Summary Card */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Typography variant="h5" component="div">
                Scan Results
              </Typography>
              <ThreatLevelChip level={threat_level} />
            </Box>
            <Typography color="textSecondary" gutterBottom>
              File: {filename}
            </Typography>
            <Typography color="textSecondary" gutterBottom>
              Scanned: {new Date(timestamp).toLocaleString()}
            </Typography>
          </CardContent>
        </Card>
      </Grid>

      {/* Deepfake Detection Results */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Deepfake Detection
            </Typography>
            <List>
              <ListItem>
                <ListItemIcon>
                  {deepfake_detection.is_deepfake ? (
                    <ErrorIcon color="error" />
                  ) : (
                    <CheckCircle color="success" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={
                    deepfake_detection.is_deepfake
                      ? 'Deepfake Detected'
                      : 'No Deepfake Detected'
                  }
                  secondary={`Confidence: ${deepfake_detection.confidence}%`}
                />
              </ListItem>
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* Malware Analysis Results */}
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Malware Analysis
            </Typography>
            <List>
              {malware_analysis.threats.map((threat, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <Warning color="warning" />
                  </ListItemIcon>
                  <ListItemText
                    primary={threat.type}
                    secondary={`Risk Level: ${threat.risk_level}%`}
                  />
                </ListItem>
              ))}
              {malware_analysis.threats.length === 0 && (
                <ListItem>
                  <ListItemIcon>
                    <CheckCircle color="success" />
                  </ListItemIcon>
                  <ListItemText primary="No malware detected" />
                </ListItem>
              )}
            </List>
          </CardContent>
        </Card>
      </Grid>

      {/* Detailed Findings */}
      <Grid item xs={12}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Detailed Findings
            </Typography>
            <List>
              {threats_found.map((threat, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <ErrorIcon color="error" />
                  </ListItemIcon>
                  <ListItemText
                    primary={threat.description}
                    secondary={`Category: ${threat.category} | Severity: ${threat.severity}`}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default ScanResults;

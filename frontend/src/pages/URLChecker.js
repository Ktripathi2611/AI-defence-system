import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  Typography,
  Grid,
  Paper,
  Alert,
  AlertTitle,
  List,
  ListItem,
  ListItemText,
  Chip,
  LinearProgress,
  CircularProgress,
  Container,
  Card,
  CardContent,
  Divider,
  IconButton,
  Tooltip
} from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import LinkIcon from '@mui/icons-material/Link';
import DnsIcon from '@mui/icons-material/Dns';
import LockIcon from '@mui/icons-material/Lock';
import WarningIcon from '@mui/icons-material/Warning';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';
import { useTheme } from '@mui/material/styles';
import securityService from '../services/securityService';

const URLChecker = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [analysisStartTime, setAnalysisStartTime] = useState(null);
  const theme = useTheme();

  const handleCheck = async () => {
    if (!url) {
      setError('Please enter a URL');
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    setAnalysisStartTime(Date.now());

    try {
      const data = await securityService.analyzeURL(url);
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const ResultCard = ({ title, icon, severity = 'info', children }) => (
    <Card 
      sx={{ 
        height: '100%',
        bgcolor: 'rgba(0, 0, 0, 0.2)',
        backdropFilter: 'blur(10px)',
        border: 1,
        borderColor: theme.palette[severity].main + '40',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: `0 4px 20px ${theme.palette[severity].main}40`
        }
      }}
    >
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          {icon}
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            {title}
          </Typography>
          <Tooltip title={`Learn more about ${title}`}>
            <IconButton size="small">
              <HelpOutlineIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
        <Divider sx={{ mb: 2 }} />
        {children}
      </CardContent>
    </Card>
  );

  const SecurityScore = ({ score }) => (
    <Box sx={{ textAlign: 'center', my: 2 }}>
      <Typography variant="h3" gutterBottom>
        {score}%
      </Typography>
      <LinearProgress
        variant="determinate"
        value={score}
        sx={{
          height: 10,
          borderRadius: 5,
          bgcolor: 'rgba(0,0,0,0.1)',
          '& .MuiLinearProgress-bar': {
            borderRadius: 5,
            bgcolor: (theme) => {
              if (score >= 80) return theme.palette.success.main;
              if (score >= 60) return theme.palette.warning.main;
              return theme.palette.error.main;
            }
          }
        }}
      />
    </Box>
  );

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Paper 
        elevation={0}
        sx={{ 
          p: 4, 
          bgcolor: 'rgba(0, 0, 0, 0.2)',
          backdropFilter: 'blur(10px)',
          borderRadius: 2
        }}
      >
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography variant="h3" component="h1" gutterBottom>
            <SecurityIcon fontSize="large" sx={{ mr: 2, verticalAlign: 'bottom' }} />
            URL Security Analyzer
          </Typography>
          <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 4 }}>
            Check any URL for potential security threats and analyze its safety score
          </Typography>
        </Box>

        <Box sx={{ maxWidth: 600, mx: 'auto', mb: 4 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Enter URL to analyze (e.g., https://example.com)"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            error={!!error}
            helperText={error}
            InputProps={{
              startAdornment: <LinkIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              sx: { 
                bgcolor: 'rgba(255, 255, 255, 0.05)',
                '&:hover': {
                  bgcolor: 'rgba(255, 255, 255, 0.08)'
                }
              }
            }}
            sx={{ mb: 2 }}
          />
          <Button
            fullWidth
            variant="contained"
            onClick={handleCheck}
            disabled={loading}
            startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <DnsIcon />}
            sx={{
              height: 48,
              bgcolor: theme.palette.primary.main,
              '&:hover': {
                bgcolor: theme.palette.primary.dark
              }
            }}
          >
            {loading ? 'Analyzing...' : 'Analyze URL'}
          </Button>
        </Box>

        {loading && (
          <Box sx={{ width: '100%', mt: 2 }}>
            <LinearProgress />
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mt: 1 }}>
              Analyzing URL security... This may take a few moments
            </Typography>
          </Box>
        )}

        {result && (
          <Box sx={{ mt: 4 }}>
            <Grid container spacing={3}>
              {/* Overall Security Score */}
              <Grid item xs={12}>
                <ResultCard 
                  title="Overall Security Score"
                  icon={<SecurityIcon color="primary" />}
                  severity={result.security.overallScore >= 80 ? 'success' : result.security.overallScore >= 60 ? 'warning' : 'error'}
                >
                  <SecurityScore score={result.security.overallScore} />
                </ResultCard>
              </Grid>

              {/* HTTP Response */}
              <Grid item xs={12} md={6}>
                <ResultCard 
                  title="HTTP Response"
                  icon={<LockIcon />}
                  severity={result.httpResponse?.error ? 'warning' : 'info'}
                >
                  {result.httpResponse?.error ? (
                    <Alert 
                      severity="warning"
                      sx={{ 
                        bgcolor: 'rgba(237, 108, 2, 0.1)',
                        color: theme.palette.warning.main 
                      }}
                    >
                      <AlertTitle>Warning</AlertTitle>
                      {result.httpResponse.error}
                      {result.httpResponse.details && (
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          {result.httpResponse.details}
                        </Typography>
                      )}
                    </Alert>
                  ) : (
                    <List dense>
                      <ListItem>
                        <ListItemText 
                          primary="Status"
                          secondary={`${result.httpResponse?.status} ${result.httpResponse?.statusText}`}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Server"
                          secondary={result.httpResponse?.server || 'Not specified'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Content Type"
                          secondary={result.httpResponse?.contentType || 'Not specified'}
                        />
                      </ListItem>
                      <ListItem>
                        <ListItemText 
                          primary="Response Time"
                          secondary={result.httpResponse?.responseTime}
                        />
                      </ListItem>
                    </List>
                  )}
                </ResultCard>
              </Grid>

              {/* Security Checks */}
              <Grid item xs={12} md={6}>
                <ResultCard 
                  title="Security Checks"
                  icon={<WarningIcon />}
                  severity={
                    result.security.safeBrowsing?.error || 
                    result.security.urlScan?.error || 
                    result.security.virusTotal?.error ? 'warning' : 'success'
                  }
                >
                  <List dense>
                    {/* Google Safe Browsing */}
                    <ListItem>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {result.security.safeBrowsing?.error ? (
                              <ErrorIcon color="error" fontSize="small" />
                            ) : result.security.safeBrowsing?.safe ? (
                              <CheckCircleIcon color="success" fontSize="small" />
                            ) : (
                              <WarningIcon color="warning" fontSize="small" />
                            )}
                            Google Safe Browsing
                          </Box>
                        }
                        secondary={
                          result.security.safeBrowsing?.error ||
                          (result.security.safeBrowsing?.safe ? 'Safe' : 'Potentially harmful')
                        }
                      />
                    </ListItem>

                    {/* URLScan */}
                    <ListItem>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {result.security.urlScan?.error ? (
                              <ErrorIcon color="error" fontSize="small" />
                            ) : (
                              <CheckCircleIcon color="success" fontSize="small" />
                            )}
                            URLScan Analysis
                          </Box>
                        }
                        secondary={
                          result.security.urlScan?.error ||
                          `Score: ${result.security.urlScan?.score || 0}/100`
                        }
                      />
                    </ListItem>

                    {/* VirusTotal */}
                    <ListItem>
                      <ListItemText
                        primary={
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            {result.security.virusTotal?.error ? (
                              <ErrorIcon color="error" fontSize="small" />
                            ) : (
                              <CheckCircleIcon color="success" fontSize="small" />
                            )}
                            VirusTotal Scan
                          </Box>
                        }
                        secondary={
                          result.security.virusTotal?.error ||
                          `${result.security.virusTotal?.positives || 0} detections out of ${result.security.virusTotal?.total || 0}`
                        }
                      />
                    </ListItem>
                  </List>
                </ResultCard>
              </Grid>

              {/* URL Details */}
              <Grid item xs={12}>
                <ResultCard 
                  title="URL Details"
                  icon={<LinkIcon />}
                  severity="info"
                >
                  <Grid container spacing={2}>
                    <Grid item xs={12} md={6}>
                      <List dense>
                        <ListItem>
                          <ListItemText 
                            primary="Protocol"
                            secondary={result.urlBreakdown?.protocol || 'N/A'}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText 
                            primary="Hostname"
                            secondary={result.urlBreakdown?.hostname || 'N/A'}
                          />
                        </ListItem>
                      </List>
                    </Grid>
                    <Grid item xs={12} md={6}>
                      <List dense>
                        <ListItem>
                          <ListItemText 
                            primary="Path"
                            secondary={result.urlBreakdown?.pathname || '/'}
                          />
                        </ListItem>
                        <ListItem>
                          <ListItemText 
                            primary="Query Parameters"
                            secondary={
                              Object.keys(result.urlBreakdown?.query || {}).length > 0
                                ? JSON.stringify(result.urlBreakdown.query)
                                : 'None'
                            }
                          />
                        </ListItem>
                      </List>
                    </Grid>
                  </Grid>
                </ResultCard>
              </Grid>
            </Grid>

            {analysisStartTime && (
              <Typography 
                variant="body2" 
                color="text.secondary" 
                align="center" 
                sx={{ mt: 3 }}
              >
                Analysis completed in {((Date.now() - analysisStartTime) / 1000).toFixed(2)} seconds
              </Typography>
            )}
          </Box>
        )}
      </Paper>
    </Container>
  );
};

export default URLChecker;

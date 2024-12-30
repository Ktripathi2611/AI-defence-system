import React, { useState } from 'react';
import {
  Container,
  Typography,
  TextField,
  Button,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Box,
  CircularProgress,
  Grid,
} from '@mui/material';
import {
  Send as SendIcon,
} from '@mui/icons-material';
import config from '../config';

const ReportThreat = () => {
  const [formData, setFormData] = useState({
    url: '',
    type: '',
    description: '',
    evidence: '',
    impact: 'low',
  });

  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  const threatTypes = [
    'Phishing',
    'Malware',
    'Scam',
    'Deepfake',
    'Impersonation',
    'Cryptocurrency Fraud',
    'Other',
  ];

  const impactLevels = [
    { value: 'low', label: 'Low' },
    { value: 'medium', label: 'Medium' },
    { value: 'high', label: 'High' },
    { value: 'critical', label: 'Critical' },
  ];

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError(null);
    setSuccess(false);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      const response = await fetch(`${config.apiUrl}${config.endpoints.report}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (response.ok) {
        setFormData({
          url: '',
          type: '',
          description: '',
          evidence: '',
          impact: 'low',
        });
        setMessage({ text: 'Threat reported successfully!', type: 'success' });
      } else {
        setMessage({ text: 'Failed to report threat. Please try again.', type: 'error' });
      }
    } catch (error) {
      console.error('Error reporting threat:', error);
      setMessage({ text: 'An error occurred while reporting the threat.', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom color="white">
        Report a Threat
      </Typography>

      <Card sx={{ bgcolor: 'rgba(0, 0, 0, 0.2)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <CardContent>
          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="URL or Source"
                  name="url"
                  value={formData.url}
                  onChange={handleChange}
                  variant="outlined"
                  required
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: 'white',
                      '& fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.23)',
                      },
                    },
                    '& .MuiInputLabel-root': {
                      color: 'rgba(255, 255, 255, 0.7)',
                    },
                  }}
                />
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    Threat Type
                  </InputLabel>
                  <Select
                    name="type"
                    value={formData.type}
                    onChange={handleChange}
                    sx={{
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'rgba(255, 255, 255, 0.23)',
                      },
                    }}
                  >
                    {threatTypes.map((type) => (
                      <MenuItem key={type} value={type.toLowerCase()}>
                        {type}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12} sm={6}>
                <FormControl fullWidth required>
                  <InputLabel sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    Impact Level
                  </InputLabel>
                  <Select
                    name="impact"
                    value={formData.impact}
                    onChange={handleChange}
                    sx={{
                      color: 'white',
                      '& .MuiOutlinedInput-notchedOutline': {
                        borderColor: 'rgba(255, 255, 255, 0.23)',
                      },
                    }}
                  >
                    {impactLevels.map((level) => (
                      <MenuItem key={level.value} value={level.value}>
                        {level.label}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  multiline
                  rows={4}
                  required
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: 'white',
                      '& fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.23)',
                      },
                    },
                    '& .MuiInputLabel-root': {
                      color: 'rgba(255, 255, 255, 0.7)',
                    },
                  }}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Evidence (URLs, screenshots, etc.)"
                  name="evidence"
                  value={formData.evidence}
                  onChange={handleChange}
                  multiline
                  rows={2}
                  sx={{
                    '& .MuiOutlinedInput-root': {
                      color: 'white',
                      '& fieldset': {
                        borderColor: 'rgba(255, 255, 255, 0.23)',
                      },
                    },
                    '& .MuiInputLabel-root': {
                      color: 'rgba(255, 255, 255, 0.7)',
                    },
                  }}
                />
              </Grid>

              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} /> : <SendIcon />}
                  sx={{ minWidth: 200 }}
                >
                  {loading ? 'Submitting...' : 'Submit Report'}
                </Button>
              </Grid>
            </Grid>
          </Box>

          {message && (
            <Alert severity={message.type} sx={{ mt: 3 }}>
              {message.text}
            </Alert>
          )}
        </CardContent>
      </Card>
    </Container>
  );
};

export default ReportThreat;

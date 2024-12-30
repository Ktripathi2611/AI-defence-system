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
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Community() {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    type: '',
    evidence: '',
    contact: '',
  });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      await axios.post(`${API_URL}/api/community/report`, formData);
      setSuccess(true);
      setFormData({
        title: '',
        description: '',
        type: '',
        evidence: '',
        contact: '',
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while submitting the report');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Community Reporting
      </Typography>

      <Card>
        <CardContent>
          <form onSubmit={handleSubmit}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Report Type</InputLabel>
                  <Select
                    name="type"
                    value={formData.type}
                    label="Report Type"
                    onChange={handleChange}
                    required
                  >
                    <MenuItem value="spam">Spam</MenuItem>
                    <MenuItem value="phishing">Phishing</MenuItem>
                    <MenuItem value="malware">Malware</MenuItem>
                    <MenuItem value="deepfake">Deepfake</MenuItem>
                    <MenuItem value="other">Other</MenuItem>
                  </Select>
                </FormControl>
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  required
                />
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
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Evidence (URLs, file hashes, etc.)"
                  name="evidence"
                  value={formData.evidence}
                  onChange={handleChange}
                  multiline
                  rows={2}
                />
              </Grid>

              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Contact Information (optional)"
                  name="contact"
                  value={formData.contact}
                  onChange={handleChange}
                  helperText="Your contact information will be kept confidential"
                />
              </Grid>

              <Grid item xs={12}>
                <Button
                  type="submit"
                  variant="contained"
                  color="primary"
                  disabled={loading}
                  startIcon={<SendIcon />}
                >
                  Submit Report
                </Button>
              </Grid>
            </Grid>
          </form>

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

          {success && (
            <Alert severity="success" sx={{ mt: 2 }}>
              Your report has been submitted successfully. Thank you for helping keep our community safe!
            </Alert>
          )}
        </CardContent>
      </Card>
    </Box>
  );
}

export default Community;

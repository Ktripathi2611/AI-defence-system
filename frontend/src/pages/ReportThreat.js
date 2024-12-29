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
} from '@mui/material';
import ReportIcon from '@mui/icons-material/Report';

const ReportThreat = () => {
  const [formData, setFormData] = useState({
    url: '',
    type: '',
    description: '',
  });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/report/threat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();
      setResult({
        success: true,
        message: `Thank you for your report! Report ID: ${data.report_id}`,
      });
      setFormData({ url: '', type: '', description: '' });
    } catch (error) {
      setResult({
        success: false,
        message: 'Failed to submit report. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Report a Threat
      </Typography>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="body1" paragraph>
            Help protect our community by reporting suspicious activities,
            phishing attempts, or potential cyber threats.
          </Typography>

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="URL or Source"
              name="url"
              value={formData.url}
              onChange={handleChange}
              margin="normal"
              helperText="Enter the suspicious URL or source of the threat"
            />

            <FormControl fullWidth margin="normal">
              <InputLabel>Threat Type</InputLabel>
              <Select
                name="type"
                value={formData.type}
                onChange={handleChange}
                label="Threat Type"
                required
              >
                <MenuItem value="phishing">Phishing Attempt</MenuItem>
                <MenuItem value="malware">Malware</MenuItem>
                <MenuItem value="scam">Scam</MenuItem>
                <MenuItem value="deepfake">Deepfake</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              margin="normal"
              multiline
              rows={4}
              helperText="Provide details about the threat"
            />

            <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center' }}>
              <Button
                type="submit"
                variant="contained"
                size="large"
                disabled={loading}
                startIcon={<ReportIcon />}
              >
                {loading ? 'Submitting...' : 'Submit Report'}
              </Button>
            </Box>
          </form>
        </CardContent>
      </Card>

      {result && (
        <Alert severity={result.success ? 'success' : 'error'} sx={{ mt: 2 }}>
          {result.message}
        </Alert>
      )}

      <Card sx={{ mt: 4 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            What Happens Next?
          </Typography>
          <Typography variant="body2" color="text.secondary">
            1. Our AI system will analyze your report
            <br />
            2. The threat will be verified by our security team
            <br />
            3. If confirmed, it will be added to our threat database
            <br />
            4. Other users will be protected from this threat
          </Typography>
        </CardContent>
      </Card>
    </Container>
  );
};

export default ReportThreat;

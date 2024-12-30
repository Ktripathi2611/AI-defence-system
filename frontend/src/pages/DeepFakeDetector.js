import React, { useState } from 'react';
import {
  Container,
  Typography,
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Alert,
} from '@mui/material';
import { CloudUpload as CloudUploadIcon } from '@mui/icons-material';
import config from '../config';

const DeepFakeDetector = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file && (file.type.startsWith('image/') || file.type.startsWith('video/'))) {
      setSelectedFile(file);
      setError(null);
    } else {
      setError('Please select a valid image or video file');
      setSelectedFile(null);
    }
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please select a file to analyze');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${config.API_URL}/analyze/media`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze media');
      }

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to analyze media. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" gutterBottom color="white">
        Deepfake Detection
      </Typography>

      <Card sx={{ bgcolor: 'rgba(0, 0, 0, 0.2)', mb: 3 }}>
        <CardContent>
          <Box sx={{ textAlign: 'center', py: 3 }}>
            <input
              accept="image/*,video/*"
              style={{ display: 'none' }}
              id="media-file"
              type="file"
              onChange={handleFileSelect}
              disabled={loading}
            />
            <label htmlFor="media-file">
              <Button
                variant="outlined"
                component="span"
                startIcon={<CloudUploadIcon />}
                disabled={loading}
                sx={{
                  borderColor: 'rgba(255, 255, 255, 0.23)',
                  color: 'white',
                  '&:hover': {
                    borderColor: 'white',
                  },
                }}
              >
                Upload Media File
              </Button>
            </label>
            {selectedFile && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                Selected: {selectedFile.name}
              </Typography>
            )}
          </Box>

          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
            <Button
              variant="contained"
              onClick={handleAnalyze}
              disabled={!selectedFile || loading}
              sx={{ minWidth: 200 }}
            >
              {loading ? (
                <CircularProgress size={24} color="inherit" />
              ) : (
                'Analyze'
              )}
            </Button>
          </Box>
        </CardContent>
      </Card>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {result && (
        <Card sx={{ bgcolor: 'rgba(0, 0, 0, 0.2)' }}>
          <CardContent>
            <Typography variant="h6" color="white" gutterBottom>
              Analysis Results
            </Typography>
            
            <Box sx={{ mt: 2 }}>
              <Typography color="white" gutterBottom>
                Confidence Score: {result.confidence_score}%
              </Typography>
              <Typography color="white" gutterBottom>
                Classification: {result.is_deepfake ? 'Potential Deepfake' : 'Likely Authentic'}
              </Typography>
              {result.detection_details && (
                <Typography color="text.secondary">
                  {result.detection_details}
                </Typography>
              )}
            </Box>
          </CardContent>
        </Card>
      )}
    </Container>
  );
};

export default DeepFakeDetector;

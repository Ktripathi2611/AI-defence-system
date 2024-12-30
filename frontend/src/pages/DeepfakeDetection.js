import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Button,
  Typography,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import { Warning as WarningIcon, CheckCircle as CheckCircleIcon } from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function DeepfakeDetection() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreview(reader.result);
      };
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a file to analyze');
      return;
    }

    setLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post(
        `${API_URL}/api/deepfake/analyze/${file.type.includes('video') ? 'video' : 'image'}`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'An error occurred while analyzing the file');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Deepfake Detection
      </Typography>
      
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Analyze Image or Video
          </Typography>
          
          <input
            accept="image/*,video/*"
            style={{ display: 'none' }}
            id="file-upload"
            type="file"
            onChange={handleFileChange}
          />
          <label htmlFor="file-upload">
            <Button variant="contained" component="span" sx={{ mr: 2 }}>
              Upload File
            </Button>
          </label>
          {file && (
            <Button
              variant="contained"
              color="primary"
              onClick={handleAnalyze}
              disabled={loading}
            >
              Analyze
            </Button>
          )}

          {preview && (
            <Box sx={{ mt: 2 }}>
              {file.type.includes('image') ? (
                <img src={preview} alt="Preview" style={{ maxWidth: '100%', maxHeight: 300 }} />
              ) : (
                <video controls style={{ maxWidth: '100%', maxHeight: 300 }}>
                  <source src={preview} type={file.type} />
                  Your browser does not support the video tag.
                </video>
              )}
            </Box>
          )}

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
                severity={result.is_deepfake ? 'warning' : 'success'}
                icon={result.is_deepfake ? <WarningIcon /> : <CheckCircleIcon />}
              >
                {result.is_deepfake
                  ? 'This file shows signs of manipulation'
                  : 'No signs of manipulation detected'}
              </Alert>

              <Typography variant="h6" sx={{ mt: 2 }}>
                Analysis Details
              </Typography>
              <List>
                <ListItem>
                  <ListItemIcon>
                    <WarningIcon color={result.is_deepfake ? 'warning' : 'success'} />
                  </ListItemIcon>
                  <ListItemText
                    primary="Confidence Score"
                    secondary={`${(result.confidence * 100).toFixed(1)}%`}
                  />
                </ListItem>
                {result.details?.anomalies?.map((anomaly, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <WarningIcon color="warning" />
                    </ListItemIcon>
                    <ListItemText primary={anomaly} />
                  </ListItem>
                ))}
              </List>

              <Typography variant="h6" sx={{ mt: 2 }}>
                Safety Recommendations
              </Typography>
              <List>
                {result.safety_recommendations?.map((tip, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <CheckCircleIcon color="info" />
                    </ListItemIcon>
                    <ListItemText primary={tip} />
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

export default DeepfakeDetection;

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
import CloudUploadIcon from '@mui/icons-material/CloudUpload';

const DeepFakeDetector = () => {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

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

  const handleSubmit = async () => {
    if (!file) return;

    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/analyze/media', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        error: 'Failed to analyze media. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        Deepfake Detection
      </Typography>

      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="body1" gutterBottom>
            Upload an image or video to check if it's authentic or AI-generated.
          </Typography>

          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              gap: 2,
              mt: 2,
            }}
          >
            <Button
              variant="outlined"
              component="label"
              startIcon={<CloudUploadIcon />}
            >
              Upload Media
              <input
                type="file"
                hidden
                accept="image/*,video/*"
                onChange={handleFileChange}
              />
            </Button>

            {preview && (
              <Box 
                sx={{ 
                  mt: 2, 
                  maxWidth: '100%',
                  display: 'flex',
                  justifyContent: 'center',
                  alignItems: 'center',
                  minHeight: '200px',
                  border: '2px dashed #ccc',
                  borderRadius: '8px',
                  padding: '16px'
                }}
              >
                {file?.type.startsWith('image/') ? (
                  <img
                    src={preview}
                    alt="Preview"
                    style={{ 
                      maxWidth: '100%', 
                      maxHeight: '400px',
                      objectFit: 'contain'
                    }}
                  />
                ) : file?.type.startsWith('video/') ? (
                  <video
                    controls
                    style={{ 
                      maxWidth: '100%', 
                      maxHeight: '400px'
                    }}
                  >
                    <source src={preview} type={file.type} />
                    Your browser does not support the video tag.
                  </video>
                ) : (
                  <Typography color="error">
                    Unsupported file type. Please upload an image or video.
                  </Typography>
                )}
              </Box>
            )}

            <Button
              variant="contained"
              color="primary"
              onClick={handleSubmit}
              disabled={!file || loading}
              sx={{ mt: 2 }}
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

      {result && (
        <Box sx={{ mt: 3 }}>
          <Alert 
            severity={result.is_fake ? "error" : "success"}
            sx={{ mb: 2 }}
          >
            {result.is_fake 
              ? "This media appears to be AI-generated" 
              : "This media appears to be authentic"}
          </Alert>
          
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Analysis Results
              </Typography>
              <Typography>
                Confidence: {(result.confidence * 100).toFixed(1)}%
              </Typography>
              {result.analysis_details && (
                <>
                  <Typography variant="subtitle1" sx={{ mt: 2 }}>
                    Technical Details:
                  </Typography>
                  <ul>
                    {Object.entries(result.analysis_details).map(([key, value]) => (
                      <li key={key}>
                        {key.split('_').map(word => 
                          word.charAt(0).toUpperCase() + word.slice(1)
                        ).join(' ')}: {typeof value === 'number' ? value.toFixed(2) : value}
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </CardContent>
          </Card>
        </Box>
      )}
    </Container>
  );
};

export default DeepFakeDetector;

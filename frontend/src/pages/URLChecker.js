import React, { useState } from 'react';
import {
  Container,
  TextField,
  Button,
  Card,
  CardContent,
  Typography,
  Box,
  Alert,
  CircularProgress
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

const URLChecker = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/analyze/url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const data = await response.json();
      setResult(data);
    } catch (error) {
      setResult({
        status: 'error',
        message: 'Failed to analyze URL. Please try again.',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="md" sx={{ mt: 4, mb: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>
        URL Security Checker
      </Typography>

      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', gap: 2, mb: 4 }}>
          <TextField
            fullWidth
            label="Enter URL to check"
            variant="outlined"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            disabled={loading}
          />
          <Button
            type="submit"
            variant="contained"
            startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
            disabled={loading || !url}
          >
            Check
          </Button>
        </Box>
      </form>

      {result && (
        <Card>
          <CardContent>
            {result.status === 'error' ? (
              <Alert severity="error">{result.message}</Alert>
            ) : (
              <>
                <Alert
                  severity={result.threat_level > 0.7 ? 'error' : 'success'}
                  sx={{ mb: 2 }}
                >
                  {result.threat_level > 0.7
                    ? 'This URL appears to be dangerous!'
                    : 'This URL appears to be safe.'}
                </Alert>
                <Typography variant="body1" gutterBottom>
                  Threat Level: {(result.threat_level * 100).toFixed(1)}%
                </Typography>
                <Typography variant="body1" gutterBottom>
                  Type: {result.type}
                </Typography>
                <Typography variant="body1">
                  Details: {result.details}
                </Typography>
              </>
            )}
          </CardContent>
        </Card>
      )}
    </Container>
  );
};

export default URLChecker;

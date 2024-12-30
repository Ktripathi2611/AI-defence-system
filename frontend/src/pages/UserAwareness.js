import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Grid,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  School as SchoolIcon,
  Lightbulb as LightbulbIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function UserAwareness() {
  const [tips, setTips] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSecurityTips();
  }, []);

  const fetchSecurityTips = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/awareness/tips`);
      setTips(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load security tips');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Alert severity="error" sx={{ mt: 2 }}>
        {error}
      </Alert>
    );
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        User Awareness Training
      </Typography>

      <Grid container spacing={3}>
        {tips.map((category, index) => (
          <Grid item xs={12} md={6} key={index}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                  <SchoolIcon sx={{ mr: 1 }} />
                  {category.category}
                </Typography>

                <List>
                  {category.tips.map((tip, tipIndex) => (
                    <ListItem key={tipIndex}>
                      <ListItemIcon>
                        <LightbulbIcon color="primary" />
                      </ListItemIcon>
                      <ListItemText
                        primary={tip.title}
                        secondary={tip.description}
                      />
                    </ListItem>
                  ))}
                </List>

                <Box sx={{ mt: 2 }}>
                  {category.tags.map((tag, tagIndex) => (
                    <Chip
                      key={tagIndex}
                      icon={<SecurityIcon />}
                      label={tag}
                      variant="outlined"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default UserAwareness;

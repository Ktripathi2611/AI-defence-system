import React from 'react';
import { AppBar, Toolbar, Typography, Button, Box } from '@mui/material';
import { Link } from 'react-router-dom';
import ShieldIcon from '@mui/icons-material/Shield';
import SearchIcon from '@mui/icons-material/Search';
import ReportIcon from '@mui/icons-material/Report';
import SchoolIcon from '@mui/icons-material/School';

const Navbar = () => {
  return (
    <AppBar position="static">
      <Toolbar>
        <ShieldIcon sx={{ mr: 2 }} />
        <Typography variant="h6" component={Link} to="/" sx={{ flexGrow: 1, textDecoration: 'none', color: 'inherit' }}>
          AI Defense System
        </Typography>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            color="inherit"
            component={Link}
            to="/url-checker"
            startIcon={<SearchIcon />}
          >
            URL Checker
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/deepfake-detector"
            startIcon={<SearchIcon />}
          >
            Deepfake Detector
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/awareness"
            startIcon={<SchoolIcon />}
          >
            Learn
          </Button>
          <Button
            color="inherit"
            component={Link}
            to="/report"
            startIcon={<ReportIcon />}
          >
            Report Threat
          </Button>
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;

import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Box,
  IconButton,
} from '@mui/material';
import {
  Security as SecurityIcon,
  Search as SearchIcon,
  VideoCall as VideoCallIcon,
  School as SchoolIcon,
  Report as ReportIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

const Navbar = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  const navItems = [
    { label: 'URL CHECKER', icon: <SearchIcon />, path: '/url-checker' },
    { label: 'DEEPFAKE DETECTOR', icon: <VideoCallIcon />, path: '/deepfake-detector' },
    { label: 'THREAT AWARENESS', icon: <SchoolIcon />, path: '/awareness' },
    { label: 'REPORT THREAT', icon: <ReportIcon />, path: '/report' },
  ];

  return (
    <AppBar position="fixed" sx={{ bgcolor: '#1E1E1E', boxShadow: 'none', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
      <Toolbar sx={{ justifyContent: 'space-between' }}>
        {/* Logo and Brand */}
        <Box 
          sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            cursor: 'pointer' 
          }} 
          onClick={() => navigate('/')}
        >
          <SecurityIcon sx={{ fontSize: 32, mr: 1, color: 'primary.main' }} />
          <Typography variant="h6" component="div" sx={{ flexGrow: 0, fontWeight: 'bold', color: 'white' }}>
            AI Defense System
          </Typography>
        </Box>

        {/* Navigation Items */}
        <Box sx={{ display: 'flex', gap: 2 }}>
          {navItems.map((item) => (
            <Button
              key={item.path}
              startIcon={item.icon}
              onClick={() => navigate(item.path)}
              sx={{
                color: isActive(item.path) ? 'primary.main' : 'white',
                '&:hover': {
                  color: 'primary.main',
                },
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>

        {/* Settings */}
        <IconButton color="inherit">
          <SettingsIcon />
        </IconButton>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;

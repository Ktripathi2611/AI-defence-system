import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import { Box } from '@mui/material';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import URLChecker from './pages/URLChecker';
import DeepFakeDetector from './pages/DeepFakeDetector';
import ThreatAwareness from './pages/ThreatAwareness';
import ReportThreat from './pages/ReportThreat';
import './styles/global.css';

const darkTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3',
    },
    background: {
      default: '#121212',
      paper: '#1E1E1E',
    },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
    },
    h6: {
      fontWeight: 500,
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={darkTheme}>
      <Router>
        <Box sx={{ 
          minHeight: '100vh',
          bgcolor: 'background.default',
          display: 'flex',
          flexDirection: 'column'
        }}>
          <Navbar />
          <Box component="main" sx={{ 
            flexGrow: 1,
            pt: '64px', // Height of navbar
            minHeight: 'calc(100vh - 64px)',
          }}>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/url-checker" element={<URLChecker />} />
              <Route path="/deepfake-detector" element={<DeepFakeDetector />} />
              <Route path="/awareness" element={<ThreatAwareness />} />
              <Route path="/report" element={<ReportThreat />} />
            </Routes>
          </Box>
        </Box>
      </Router>
    </ThemeProvider>
  );
}

export default App;

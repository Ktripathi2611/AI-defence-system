import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Components
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import SpamDetection from './pages/SpamDetection';
import DeepfakeDetection from './pages/DeepfakeDetection';
import ThreatAnalysis from './pages/ThreatAnalysis';
import UserAwareness from './pages/UserAwareness';
import Community from './pages/Community';

// Create a theme instance
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#f5f5f5',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      'Arial',
      'sans-serif',
    ].join(','),
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
        },
      },
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/spam-detection" element={<SpamDetection />} />
            <Route path="/deepfake-detection" element={<DeepfakeDetection />} />
            <Route path="/threat-analysis" element={<ThreatAnalysis />} />
            <Route path="/user-awareness" element={<UserAwareness />} />
            <Route path="/community" element={<Community />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;

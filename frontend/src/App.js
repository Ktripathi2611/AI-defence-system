import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Navbar from './components/Navbar';
import Dashboard from './pages/Dashboard';
import URLChecker from './pages/URLChecker';
import DeepFakeDetector from './pages/DeepFakeDetector';
import ThreatAwareness from './pages/ThreatAwareness';
import ReportThreat from './pages/ReportThreat';

const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#f50057',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <div className="App">
          <Navbar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/url-checker" element={<URLChecker />} />
            <Route path="/deepfake-detector" element={<DeepFakeDetector />} />
            <Route path="/awareness" element={<ThreatAwareness />} />
            <Route path="/report" element={<ReportThreat />} />
          </Routes>
        </div>
      </Router>
    </ThemeProvider>
  );
}

export default App;

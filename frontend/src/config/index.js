const config = {
  apiUrl: process.env.REACT_APP_API_URL || 'http://localhost:3001',
  endpoints: {
    upload: process.env.REACT_APP_UPLOAD_ENDPOINT || '/api/upload',
    report: process.env.REACT_APP_REPORT_ENDPOINT || '/api/report',
    securityCheck: process.env.REACT_APP_SECURITY_CHECK_ENDPOINT || '/api/security-check',
    deepfakeCheck: process.env.REACT_APP_DEEPFAKE_CHECK_ENDPOINT || '/api/deepfake-check',
  },
  wsUrl: process.env.REACT_APP_WS_URL || 'ws://localhost:3001',
};

export default config;

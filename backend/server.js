require('dotenv').config();
const express = require('express');
const cors = require('cors');
const axios = require('axios');
const whois = require('whois-json');
const dns = require('dns').promises;
const { URL } = require('url');
const cheerio = require('cheerio');

const app = express();
const port = process.env.PORT || 3001;

// Configure CORS and JSON parsing
app.use(cors({
  origin: process.env.NODE_ENV === 'production' 
    ? process.env.FRONTEND_URL 
    : ['http://localhost:3000', 'http://127.0.0.1:3000'],
  methods: ['GET', 'POST'],
  allowedHeaders: ['Content-Type']
}));
app.use(express.json());

// Configure axios defaults
const axiosInstance = axios.create({
  timeout: 10000,
  maxRedirects: 5,
  validateStatus: false,
});

// URL Analysis endpoint
app.post('/api/analyze', async (req, res) => {
  try {
    const { url } = req.body;
    if (!url) {
      return res.status(400).json({ error: 'URL is required' });
    }

    // Start timing the analysis
    const startTime = Date.now();

    // Parse and validate URL
    let parsedUrl;
    try {
      parsedUrl = new URL(url.startsWith('http') ? url : `https://${url}`);
    } catch (error) {
      return res.status(400).json({ error: 'Invalid URL format' });
    }

    // Prepare URL breakdown
    const urlBreakdown = {
      protocol: parsedUrl.protocol,
      hostname: parsedUrl.hostname,
      pathname: parsedUrl.pathname,
      query: Object.fromEntries(parsedUrl.searchParams),
      hash: parsedUrl.hash
    };

    // Parallel execution of all checks with proper error handling
    const [httpResponse, dnsInfo, whoisData, pageData] = await Promise.allSettled([
      // HTTP Response Check
      (async () => {
        try {
          const response = await axiosInstance.get(parsedUrl.href);
          return {
            status: response.status,
            statusText: response.statusText,
            headers: response.headers,
            contentType: response.headers['content-type'],
            responseTime: Date.now() - startTime
          };
        } catch (error) {
          if (error.response) {
            return {
              status: error.response.status,
              statusText: error.response.statusText,
              headers: error.response.headers,
              contentType: error.response.headers['content-type'],
              responseTime: Date.now() - startTime
            };
          }
          throw new Error(error.message);
        }
      })(),

      // DNS Resolution
      (async () => {
        try {
          const ips = await dns.resolve4(parsedUrl.hostname);
          return {
            ips,
            hostname: parsedUrl.hostname
          };
        } catch (error) {
          throw new Error(`DNS lookup failed: ${error.message}`);
        }
      })(),

      // WHOIS Data
      (async () => {
        try {
          return await whois(parsedUrl.hostname);
        } catch (error) {
          throw new Error(`WHOIS lookup failed: ${error.message}`);
        }
      })(),

      // Page Content Analysis
      (async () => {
        try {
          const response = await axiosInstance.get(parsedUrl.href);
          if (response.headers['content-type']?.includes('text/html')) {
            const $ = cheerio.load(response.data);
            return {
              title: $('title').text(),
              description: $('meta[name="description"]').attr('content'),
              keywords: $('meta[name="keywords"]').attr('content'),
              links: {
                internal: $('a[href^="/"]').length,
                external: $('a[href^="http"]').length
              },
              headings: {
                h1: $('h1').length,
                h2: $('h2').length,
                h3: $('h3').length
              },
              meta: {
                ogTitle: $('meta[property="og:title"]').attr('content'),
                ogDescription: $('meta[property="og:description"]').attr('content'),
                ogImage: $('meta[property="og:image"]').attr('content'),
                twitterCard: $('meta[name="twitter:card"]').attr('content')
              }
            };
          }
          return null;
        } catch (error) {
          throw new Error(`Page analysis failed: ${error.message}`);
        }
      })()
    ]);

    // Calculate total analysis time
    const analysisTime = (Date.now() - startTime) / 1000;

    // Prepare the response with proper error handling
    const result = {
      url: parsedUrl.href,
      analysisTime,
      urlBreakdown,
      httpResponse: httpResponse.status === 'fulfilled' ? httpResponse.value : { 
        error: 'Failed to fetch HTTP response',
        details: httpResponse.reason?.message 
      },
      dnsInfo: dnsInfo.status === 'fulfilled' ? dnsInfo.value : { 
        error: 'DNS lookup failed',
        details: dnsInfo.reason?.message 
      },
      whoisData: whoisData.status === 'fulfilled' ? {
        registrar: whoisData.value?.registrar,
        creationDate: whoisData.value?.creationDate,
        expirationDate: whoisData.value?.expirationDate,
        lastUpdated: whoisData.value?.updatedDate
      } : { 
        error: 'WHOIS lookup failed',
        details: whoisData.reason?.message 
      },
      pageAnalysis: pageData.status === 'fulfilled' ? pageData.value : { 
        error: 'Page analysis failed',
        details: pageData.reason?.message 
      }
    };

    res.json(result);
  } catch (error) {
    console.error('URL analysis error:', error);
    res.status(500).json({
      error: 'Analysis failed',
      message: error.message,
      details: error.stack
    });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error('Global error handler:', err);
  res.status(500).json({
    error: 'Server error',
    message: err.message,
    details: process.env.NODE_ENV === 'development' ? err.stack : undefined
  });
});

// Start server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});

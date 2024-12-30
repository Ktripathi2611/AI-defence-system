import axios from 'axios';

class SecurityService {
  constructor() {
    // API configurations
    this.vtApiKey = '0bf081ac7871880dfc490f78575bb0ae285a2dac7fff77ec99dca514580634b5';
    this.urlscanApiKey = '786a6394-a6fe-46e9-bbad-4f71b73b485c';
    this.googleApiKey = 'AIzaSyA0ecrrZ3ZYOfe2OR-hvUYeSKPBu9dcVo0';

    // Initialize API clients
    this.urlScanClient = axios.create({
      baseURL: 'https://urlscan.io/api/v1',
      timeout: 30000,
      headers: {
        'API-Key': this.urlscanApiKey
      }
    });

    this.safeBrowsingClient = axios.create({
      baseURL: 'https://safebrowsing.googleapis.com/v4',
      timeout: 10000
    });

    this.vtClient = axios.create({
      baseURL: 'https://www.virustotal.com/vtapi/v2',
      timeout: 10000
    });

    // Rate limiting
    this.lastVTRequest = 0;
    this.lastUrlscanRequest = 0;
    this.vtMinRequestInterval = 15000;
    this.urlscanMinRequestInterval = 10000;

    // Result caching
    this.cache = new Map();
    this.cacheExpiration = 3600000; // 1 hour
    this.maxCacheSize = 1000;

    // Add response interceptor for better error handling
    const interceptor = (client) => {
      client.interceptors.response.use(
        response => response,
        error => {
          console.error('API Error:', error);
          if (error.response) {
            const status = error.response.status;
            const message = error.response.data?.message || error.response.data?.error;
            
            // Handle specific API errors
            if (status === 401) {
              throw new Error('Invalid API key. Please check your configuration.');
            } else if (status === 429) {
              throw new Error('Rate limit exceeded. Please try again later.');
            } else {
              throw new Error(message || `HTTP Error ${status}: ${this.getStatusMessage(status)}`);
            }
          } else if (error.code === 'ECONNABORTED') {
            throw new Error('Request timed out. Please try again.');
          } else if (error.request) {
            throw new Error('Network Error: Failed to get a response from the server.');
          } else {
            throw new Error('Request Error: ' + error.message);
          }
        }
      );
    };

    // Apply interceptor to all clients
    [this.urlScanClient, this.safeBrowsingClient, this.vtClient].forEach(interceptor);

    // Log API key status (without exposing keys)
    console.log('API Configuration Status:', {
      virustotal: this.vtApiKey ? 'Configured' : 'Missing',
      urlscan: this.urlscanApiKey ? 'Configured' : 'Missing',
      safebrowsing: this.googleApiKey ? 'Configured' : 'Missing'
    });

    // Initialize client for API requests
    this.client = axios.create({
      baseURL: process.env.REACT_APP_API_URL || '',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    });

    // Add response interceptor for better error handling
    this.client.interceptors.response.use(
      response => response,
      error => {
        console.error('API Error:', error);
        if (error.response) {
          const status = error.response.status;
          const message = error.response.data?.message || error.response.data?.error;
          throw new Error(message || `HTTP Error ${status}: ${this.getStatusMessage(status)}`);
        } else if (error.request) {
          throw new Error('Network Error: Failed to get a response from the server.');
        } else {
          throw new Error('Request Error: ' + error.message);
        }
      }
    );
  }

  getStatusMessage(status) {
    const messages = {
      400: 'Bad Request - Please check your input',
      401: 'Unauthorized - API key may be invalid',
      403: 'Forbidden - Check API key permissions',
      404: 'Not Found - Resource does not exist',
      429: 'Too Many Requests - Please wait and try again',
      500: 'Internal Server Error - Service is having issues',
      502: 'Bad Gateway - Service is temporarily unavailable',
      503: 'Service Unavailable - Please try again later',
      504: 'Gateway Timeout - Service took too long to respond'
    };
    return messages[status] || 'Unknown Error';
  }

  // Cache management
  getCachedResult(url) {
    const cached = this.cache.get(url);
    if (cached && Date.now() - cached.timestamp < this.cacheExpiration) {
      return cached.data;
    }
    return null;
  }

  setCachedResult(url, data) {
    if (this.cache.size >= this.maxCacheSize) {
      // Remove oldest entries
      const oldestKey = [...this.cache.keys()][0];
      this.cache.delete(oldestKey);
    }
    this.cache.set(url, { data, timestamp: Date.now() });
  }

  // New security checks
  async checkSecurityHeaders(url) {
    try {
      const response = await this.client.head(url);
      const headers = response.headers;
      const results = [];

      this.securityHeaders.forEach(header => {
        const hasHeader = headers[header.toLowerCase()];
        results.push({
          header,
          present: !!hasHeader,
          value: hasHeader || 'Not set'
        });
      });

      return {
        score: this.calculateHeaderScore(results),
        details: results,
        recommendations: this.getHeaderRecommendations(results)
      };
    } catch (error) {
      console.error('Security headers check failed:', error);
      return {
        score: 0,
        details: [],
        recommendations: ['Could not check security headers']
      };
    }
  }

  async checkTLS(domain) {
    try {
      const response = await this.client.get(`https://api.ssllabs.com/api/v3/analyze?host=${domain}&startNew=off&fromCache=on`);
      const data = response.data;

      return {
        grade: data.endpoints?.[0]?.grade || 'Unknown',
        protocol: data.endpoints?.[0]?.details?.highestProtocol || 'Unknown',
        cipherStrength: data.endpoints?.[0]?.details?.cipherStrength || 0,
        vulnerabilities: {
          heartbleed: data.endpoints?.[0]?.details?.heartbleed || false,
          poodle: data.endpoints?.[0]?.details?.poodle || false,
          freak: data.endpoints?.[0]?.details?.freak || false
        }
      };
    } catch (error) {
      console.error('TLS check failed:', error);
      return {
        grade: 'Unknown',
        protocol: 'Unknown',
        cipherStrength: 0,
        vulnerabilities: {}
      };
    }
  }

  calculateHeaderScore(headerResults) {
    let score = 100;
    const criticalHeaders = ['Strict-Transport-Security', 'Content-Security-Policy'];
    const importantHeaders = ['X-Frame-Options', 'X-Content-Type-Options'];

    headerResults.forEach(result => {
      if (!result.present) {
        if (criticalHeaders.includes(result.header)) {
          score -= 25;
        } else if (importantHeaders.includes(result.header)) {
          score -= 15;
        } else {
          score -= 10;
        }
      }
    });

    return Math.max(0, score);
  }

  getHeaderRecommendations(headerResults) {
    const recommendations = [];
    headerResults.forEach(result => {
      if (!result.present) {
        switch (result.header) {
          case 'Strict-Transport-Security':
            recommendations.push('Enable HSTS to ensure secure connections');
            break;
          case 'Content-Security-Policy':
            recommendations.push('Implement CSP to prevent XSS attacks');
            break;
          case 'X-Frame-Options':
            recommendations.push('Set X-Frame-Options to prevent clickjacking');
            break;
          case 'X-Content-Type-Options':
            recommendations.push('Enable X-Content-Type-Options to prevent MIME-type confusion');
            break;
          case 'Referrer-Policy':
            recommendations.push('Set Referrer-Policy to control information leakage');
            break;
          default:
            recommendations.push(`Consider implementing ${result.header} security header`);
        }
      }
    });
    return recommendations;
  }

  async analyzeURL(url) {
    try {
      if (!url) {
        throw new Error('URL is required');
      }

      // Ensure URL has protocol
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
      }

      console.log('Analyzing URL:', url);

      // Initialize result object
      const result = {
        url: url,
        analysisTime: new Date().toISOString(),
        urlBreakdown: null,
        httpResponse: null,
        security: {
          overallScore: 0,
          safeBrowsing: null,
          urlScan: null,
          virusTotal: null
        }
      };

      try {
        // Parse URL
        const parsedUrl = new URL(url);
        result.urlBreakdown = {
          protocol: parsedUrl.protocol,
          hostname: parsedUrl.hostname,
          pathname: parsedUrl.pathname,
          query: Object.fromEntries(parsedUrl.searchParams),
          hash: parsedUrl.hash
        };
      } catch (error) {
        result.urlBreakdown = { error: 'Invalid URL format' };
      }

      // Run HTTP check first with retry
      try {
        let retryCount = 0;
        const maxRetries = 2;
        let httpResponse = null;

        while (retryCount <= maxRetries) {
          httpResponse = await this.checkHttpResponse(url);
          if (!httpResponse.error || retryCount === maxRetries) {
            break;
          }
          retryCount++;
          await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds before retry
        }

        result.httpResponse = httpResponse;
      } catch (error) {
        result.httpResponse = { error: error.message };
      }

      // Run security checks in parallel
      const [safeBrowsing, urlscan, virusTotal] = await Promise.all([
        this.checkGoogleSafeBrowsing(url).catch(error => ({ error: error.message })),
        this.checkUrlScan(url).catch(error => ({ error: error.message })),
        this.checkVirusTotal(url).catch(error => ({ error: error.message }))
      ]);

      result.security.safeBrowsing = safeBrowsing;
      result.security.urlScan = urlscan;
      result.security.virusTotal = virusTotal;

      // Calculate overall score
      let totalScore = 0;
      let scoreCount = 0;

      if (!safeBrowsing.error) {
        totalScore += safeBrowsing.safe ? 100 : 0;
        scoreCount++;
      }

      if (!urlscan.error && typeof urlscan.score === 'number') {
        totalScore += urlscan.score;
        scoreCount++;
      }

      if (!virusTotal.error && virusTotal.total > 0) {
        const vtScore = 100 - (virusTotal.positives / virusTotal.total * 100);
        totalScore += vtScore;
        scoreCount++;
      }

      result.security.overallScore = scoreCount > 0 ? Math.round(totalScore / scoreCount) : 0;

      return result;
    } catch (error) {
      console.error('URL analysis error:', error);
      throw new Error(error.message || 'Failed to analyze URL');
    }
  }

  async checkHttpResponse(url) {
    try {
      // Add protocol if missing
      if (!url.startsWith('http://') && !url.startsWith('https://')) {
        url = 'https://' + url;
      }

      // Try direct request first
      try {
        const response = await axios({
          method: 'get',
          url: url,
          timeout: 10000,
          maxRedirects: 5,
          validateStatus: function (status) {
            return status >= 200 && status < 600; // Accept all responses to check status
          },
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
          }
        });

        return {
          status: response.status,
          statusText: response.statusText,
          headers: response.headers,
          redirected: response.request?.res?.responseUrl !== url,
          redirectUrl: response.request?.res?.responseUrl,
          contentType: response.headers['content-type'],
          server: response.headers['server'],
          secure: url.startsWith('https://'),
          responseTime: response.headers['x-response-time'] || 'N/A'
        };
      } catch (directError) {
        // If direct request fails, try through backend proxy
        console.log('Direct request failed, trying through proxy:', directError.message);
        
        const proxyResponse = await axios({
          method: 'post',
          url: '/api/proxy-request',  // Assuming you have this endpoint in your backend
          data: { url },
          timeout: 15000,
          headers: {
            'Content-Type': 'application/json'
          }
        });

        if (proxyResponse.data.error) {
          throw new Error(proxyResponse.data.error);
        }

        return {
          status: proxyResponse.data.status,
          statusText: proxyResponse.data.statusText,
          headers: proxyResponse.data.headers,
          redirected: proxyResponse.data.redirected,
          redirectUrl: proxyResponse.data.redirectUrl,
          contentType: proxyResponse.data.contentType,
          server: proxyResponse.data.server,
          secure: url.startsWith('https://'),
          responseTime: proxyResponse.data.responseTime,
          proxied: true
        };
      }
    } catch (error) {
      console.error('HTTP check error:', error);
      
      // Handle specific error cases
      if (error.code === 'ECONNABORTED') {
        return {
          error: 'Request timed out. The server took too long to respond.',
          status: 408
        };
      }
      
      if (error.code === 'ENOTFOUND') {
        return {
          error: 'Domain not found. Please check the URL and try again.',
          status: 404
        };
      }

      if (error.code === 'ECONNREFUSED') {
        return {
          error: 'Connection refused. The server is not accepting connections.',
          status: 503
        };
      }

      if (error.response) {
        // Server responded with error status code
        const errorMessage = error.response.data?.message || error.response.statusText;
        return {
          error: `Server responded with ${error.response.status}: ${errorMessage}`,
          status: error.response.status,
          statusText: error.response.statusText,
          headers: error.response.headers
        };
      }

      if (error.request) {
        // Request was made but no response received
        return {
          error: 'No response received from server. The service might be down or blocking our requests.',
          status: 503,
          details: 'Consider checking if the URL is correct and the server is accessible.'
        };
      }

      // Something else went wrong
      return {
        error: 'Failed to check URL: ' + (error.message || 'Unknown error'),
        status: 500,
        details: 'There might be a network connectivity issue or the server might be blocking our requests.'
      };
    }
  }

  async checkGoogleSafeBrowsing(url) {
    try {
      const response = await this.safeBrowsingClient.post(`/threatMatches:find?key=${this.googleApiKey}`, {
        client: {
          clientId: "url-analyzer",
          clientVersion: "1.0.0"
        },
        threatInfo: {
          threatTypes: ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
          platformTypes: ["ANY_PLATFORM"],
          threatEntryTypes: ["URL"],
          threatEntries: [{ url: url }]
        }
      });

      return {
        safe: !response.data.matches || response.data.matches.length === 0,
        threats: response.data.matches || []
      };
    } catch (error) {
      console.error('Safe Browsing API error:', error);
      return { error: 'Failed to check Google Safe Browsing: ' + (error.response?.data?.error?.message || error.message) };
    }
  }

  async checkUrlScan(url) {
    try {
      // Submit URL for scanning
      const submitResponse = await axios({
        method: 'post',
        url: 'https://urlscan.io/api/v1/scan/',
        headers: {
          'API-Key': this.urlscanApiKey,
          'Content-Type': 'application/json'
        },
        data: {
          url: url,
          visibility: 'public'
        },
        timeout: 30000
      });

      // Wait for scan to complete
      await new Promise(resolve => setTimeout(resolve, 20000));

      // Get results
      const resultResponse = await axios({
        method: 'get',
        url: `https://urlscan.io/api/v1/result/${submitResponse.data.uuid}/`,
        headers: {
          'API-Key': this.urlscanApiKey
        },
        timeout: 30000
      });

      return {
        score: resultResponse.data.verdicts?.overall?.score || 0,
        malicious: resultResponse.data.verdicts?.overall?.malicious || false,
        categories: resultResponse.data.verdicts?.overall?.categories || []
      };
    } catch (error) {
      console.error('URLScan API error:', error);
      if (error.code === 'ECONNABORTED') {
        return { error: 'Request timed out. The scan is taking longer than expected.' };
      }
      return { 
        error: error.response?.data?.message || error.response?.data?.description || 
              'Failed to scan URL. This could be due to rate limiting or network issues.' 
      };
    }
  }

  async checkVirusTotal(url) {
    try {
      // Submit URL for scanning
      const scanResponse = await axios({
        method: 'post',
        url: 'https://www.virustotal.com/vtapi/v3/urls',
        headers: {
          'x-apikey': this.vtApiKey,
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        data: `url=${encodeURIComponent(url)}`,
        timeout: 30000
      });

      if (!scanResponse.data?.data?.id) {
        throw new Error('Invalid response from VirusTotal API');
      }

      // Wait for analysis to complete
      await new Promise(resolve => setTimeout(resolve, 15000));

      // Get analysis results
      const resultResponse = await axios({
        method: 'get',
        url: `https://www.virustotal.com/vtapi/v3/analyses/${scanResponse.data.data.id}`,
        headers: {
          'x-apikey': this.vtApiKey
        },
        timeout: 30000
      });

      const stats = resultResponse.data?.data?.attributes?.stats || {};
      return {
        positives: stats.malicious || 0,
        total: (stats.malicious || 0) + (stats.harmless || 0) + (stats.suspicious || 0) + (stats.undetected || 0),
        scanDate: new Date().toISOString()
      };
    } catch (error) {
      console.error('VirusTotal API error:', error);
      if (error.code === 'ECONNABORTED') {
        return { error: 'Request timed out. The scan is taking longer than expected.' };
      }
      if (error.response?.status === 401) {
        return { error: 'Invalid API key or insufficient permissions.' };
      }
      if (error.response?.status === 429) {
        return { error: 'Rate limit exceeded. Please try again later.' };
      }
      return { 
        error: error.response?.data?.error?.message || 
              'Failed to check VirusTotal. This could be due to network issues or service unavailability.' 
      };
    }
  }

  getStatusColor(status) {
    if (!status) return 'error';
    if (status >= 200 && status < 300) return 'success';
    if (status >= 300 && status < 400) return 'info';
    if (status >= 400 && status < 500) return 'warning';
    if (status >= 500) return 'error';
    return 'default';
  }

  async checkSSL(url) {
    try {
      const analysisResult = await this.analyzeURL(url);
      return analysisResult.ssl;
    } catch (error) {
      console.error('SSL check error:', error);
      return {
        valid: false,
        error: error.message,
        domain: this.extractDomain(url)
      };
    }
  }

  extractDomain(url) {
    try {
      const urlObj = new URL(url);
      return urlObj.hostname;
    } catch {
      return url;
    }
  }

  calculateInfrastructureScore(sslCheck, headerCheck, tlsCheck) {
    let score = 100;

    // SSL penalties
    if (!sslCheck.valid) score -= 30;

    // Security headers
    score -= (100 - headerCheck.score) * 0.3;

    // TLS version and strength
    if (tlsCheck.grade !== 'A' && tlsCheck.grade !== 'A+') {
      score -= 20;
    }
    if (tlsCheck.vulnerabilities.heartbleed) score -= 30;
    if (tlsCheck.vulnerabilities.poodle) score -= 20;
    if (tlsCheck.vulnerabilities.freak) score -= 20;

    return Math.max(0, Math.round(score));
  }

  calculateReputationScore(dnsblCheck, domainAge, urlscanCheck) {
    let score = 100;

    // DNSBL listings
    score -= (100 - dnsblCheck.score) * 0.4;

    // Domain age
    if (domainAge.suspicious) score -= 30;

    // URLScan reputation
    if (urlscanCheck.score > 0) {
      score -= urlscanCheck.score * 0.3;
    }

    return Math.max(0, Math.round(score));
  }

  generateThreatReport(scores, checks) {
    const threats = [];

    // Phishing threats
    if (scores.phishing > 70) {
      threats.push({
        type: 'Phishing',
        severity: 'Critical',
        confidence: scores.phishing,
        details: this.getPhishingDetails(checks.vt, checks.dnsbl, checks.age, checks.urlscan, checks.phishing)
      });
    }

    // Malware threats
    if (scores.malware > 70) {
      threats.push({
        type: 'Malware',
        severity: 'Critical',
        confidence: scores.malware,
        details: this.getMalwareDetails(checks.vt, checks.dnsbl, checks.urlscan)
      });
    }

    // Infrastructure threats
    if (scores.infrastructure < 50) {
      threats.push({
        type: 'Infrastructure',
        severity: 'High',
        confidence: 100 - scores.infrastructure,
        details: this.getInfrastructureDetails(checks.ssl, checks.headers, checks.tls)
      });
    }

    // Reputation threats
    if (scores.reputation < 50) {
      threats.push({
        type: 'Reputation',
        severity: 'Medium',
        confidence: 100 - scores.reputation,
        details: this.getReputationDetails(checks.dnsbl, checks.age, checks.urlscan)
      });
    }

    return threats;
  }

  getInfrastructureDetails(ssl, headers, tls) {
    const details = [];

    if (!ssl.valid) {
      details.push('Invalid SSL certificate');
    }

    if (headers.score < 70) {
      details.push('Missing critical security headers');
    }

    if (tls.grade !== 'A' && tls.grade !== 'A+') {
      details.push(`TLS configuration grade: ${tls.grade}`);
    }

    Object.entries(tls.vulnerabilities).forEach(([vuln, exists]) => {
      if (exists) {
        details.push(`Vulnerable to ${vuln.toUpperCase()}`);
      }
    });

    return details.join('. ');
  }

  getReputationDetails(dnsbl, age, urlscan) {
    const details = [];

    if (dnsbl.listed) {
      details.push(dnsbl.details);
    }

    if (age.suspicious) {
      details.push(`Domain age: ${age.age} days (newly registered)`);
    }

    if (urlscan.score > 0) {
      details.push(`URLScan risk score: ${urlscan.score}`);
    }

    return details.join('. ');
  }

  generateEnhancedRecommendations({ scores, checks }) {
    const recommendations = [];
    
    // Critical security issues
    if (!checks.ssl.valid) {
      recommendations.push({
        priority: 'Critical',
        category: 'SSL/TLS',
        action: 'Do not enter sensitive information - invalid SSL certificate',
        details: 'The website\'s SSL certificate is invalid or misconfigured'
      });
    }

    if (checks.tls.vulnerabilities.heartbleed) {
      recommendations.push({
        priority: 'Critical',
        category: 'SSL/TLS',
        action: 'Server vulnerable to Heartbleed',
        details: 'The server is vulnerable to the Heartbleed bug (CVE-2014-0160)'
      });
    }

    // Security headers
    checks.headers.details.forEach(header => {
      if (!header.present) {
        recommendations.push({
          priority: 'High',
          category: 'Headers',
          action: `Implement ${header.header}`,
          details: this.getHeaderRecommendations([header])[0]
        });
      }
    });

    // Threat-specific recommendations
    if (scores.phishing > 70) {
      recommendations.push({
        priority: 'Critical',
        category: 'Phishing',
        action: 'Do not proceed - likely phishing attempt',
        details: 'Multiple security services have flagged this site as a potential phishing threat'
      });
    }

    if (scores.malware > 70) {
      recommendations.push({
        priority: 'Critical',
        category: 'Malware',
        action: 'Do not proceed - malware risk',
        details: 'This site has been associated with malware distribution'
      });
    }

    if (checks.age.suspicious) {
      recommendations.push({
        priority: 'Medium',
        category: 'Domain',
        action: 'Exercise caution - newly registered domain',
        details: `This domain was registered ${checks.age.age} days ago`
      });
    }

    // General security recommendations
    recommendations.push({
      priority: 'Low',
      category: 'General',
      action: 'Keep security software updated',
      details: 'Ensure your browser, antivirus, and operating system are up to date'
    });

    return recommendations;
  }

  async updatePhishingDatabase() {
    try {
      const response = await this.client.get('https://openphish.com/feed.txt');
      const data = response.data.split('\n');
      this.phishingDatabase = new Set(data);
      this.lastPhishingUpdate = Date.now();
    } catch (error) {
      console.error('Failed to update phishing database:', error);
    }
  }
}

// Create an instance of the service
const securityService = new SecurityService();

// Export the instance as default
export default securityService;

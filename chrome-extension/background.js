// Background script for the AI Defense System Chrome Extension

const API_URL = 'http://localhost:8000';

// Listen for navigation events
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  if (details.frameId === 0) { // Only check main frame navigation
    const url = details.url;
    try {
      const response = await fetch(`${API_URL}/analyze/url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url }),
      });

      const result = await response.json();

      if (result.threat_level > 0.7) {
        // Show warning notification
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/warning.png',
          title: 'Security Warning',
          message: `This website may be dangerous! Threat level: ${(result.threat_level * 100).toFixed(1)}%`,
        });

        // Store the threat information
        chrome.storage.local.set({
          [`threat_${Date.now()}`]: {
            url,
            threatLevel: result.threat_level,
            timestamp: Date.now(),
          },
        });
      }
    } catch (error) {
      console.error('Error analyzing URL:', error);
    }
  }
});

// Listen for messages from popup or content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getThreatHistory') {
    chrome.storage.local.get(null, (items) => {
      const threats = Object.entries(items)
        .filter(([key]) => key.startsWith('threat_'))
        .map(([_, value]) => value)
        .sort((a, b) => b.timestamp - a.timestamp);
      sendResponse({ threats });
    });
    return true; // Will respond asynchronously
  }
});

// Monitor for phishing attempts
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    // Check if the request is to a known phishing domain
    if (isPhishingDomain(details.url)) {
      return { cancel: true };
    }
  },
  { urls: ["<all_urls>"] },
  ["blocking"]
);

function isPhishingDomain(url) {
  // In a real implementation, this would check against a database of known phishing domains
  const suspiciousPatterns = [
    /\.xyz$/,
    /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/,
    /(secure|login|signin|account|verify)\d+\./,
  ];

  return suspiciousPatterns.some(pattern => pattern.test(url));
}

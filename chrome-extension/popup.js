document.addEventListener('DOMContentLoaded', async () => {
  // Update stats
  updateStats();
  
  // Analyze current page
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (tab) {
    analyzePage(tab.url);
  }
  
  // Load recent threats
  loadRecentThreats();
  
  // Add event listeners
  document.getElementById('scan-page').addEventListener('click', () => {
    if (tab) {
      analyzePage(tab.url, true);
    }
  });
  
  document.getElementById('report-threat').addEventListener('click', () => {
    window.open('http://localhost:3000/report', '_blank');
  });
});

async function updateStats() {
  const stats = await chrome.storage.local.get(['threatsBlocked', 'sitesScanned']);
  document.getElementById('threats-blocked').textContent = stats.threatsBlocked || 0;
  document.getElementById('sites-scanned').textContent = stats.sitesScanned || 0;
}

async function analyzePage(url, forceAnalysis = false) {
  const siteStatus = document.getElementById('site-status');
  siteStatus.innerHTML = '<div class="spinner"></div><p>Analyzing...</p>';
  
  try {
    const response = await fetch('http://localhost:8000/analyze/url?' + new URLSearchParams({
      url: url
    }), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      }
    });
    
    const result = await response.json();
    
    let statusHtml = '';
    if (result.is_malicious) {
      statusHtml = `
        <div class="status-warning">
          <img src="icons/warning.png" alt="Warning">
          <div class="warning-details">
            <h3>Warning: Potential Threat Detected</h3>
            <p>Confidence: ${(result.confidence * 100).toFixed(1)}%</p>
            <p>Risk Level: ${result.risk_level}</p>
            ${result.risk_factors.map(factor => `<p>• ${factor}</p>`).join('')}
          </div>
        </div>
      `;

      // Increment threats blocked
      const stats = await chrome.storage.local.get(['threatsBlocked']);
      chrome.storage.local.set({ 
        threatsBlocked: (stats.threatsBlocked || 0) + 1 
      });
    } else {
      statusHtml = `
        <div class="status-safe">
          <img src="icons/shield-check.png" alt="Safe">
          <div class="safe-details">
            <h3>Site appears to be safe</h3>
            <p>Confidence: ${((1 - result.confidence) * 100).toFixed(1)}%</p>
          </div>
        </div>
      `;
    }
    
    siteStatus.innerHTML = statusHtml;
    
    // Update scan count
    const stats = await chrome.storage.local.get(['sitesScanned']);
    chrome.storage.local.set({ 
      sitesScanned: (stats.sitesScanned || 0) + 1 
    });
    updateStats();
    
    // Store threat if malicious
    if (result.is_malicious) {
      chrome.runtime.sendMessage({ 
        action: 'addThreat',
        threat: {
          url: url,
          threatLevel: result.confidence,
          riskLevel: result.risk_level,
          timestamp: new Date().getTime()
        }
      });
    }
    
  } catch (error) {
    console.error('Analysis error:', error);
    siteStatus.innerHTML = `
      <div class="status-error">
        <img src="icons/error.png" alt="Error">
        <p>Error analyzing page. Please try again.</p>
      </div>
    `;
  }
}

async function loadRecentThreats() {
  const threatsList = document.getElementById('threats-list');
  
  chrome.runtime.sendMessage({ action: 'getThreatHistory' }, (response) => {
    if (!response || !response.threats || response.threats.length === 0) {
      threatsList.innerHTML = '<p class="no-threats">No recent threats detected</p>';
      return;
    }
    
    const threatsHtml = response.threats
      .slice(0, 5)
      .map(threat => `
        <div class="threat-item">
          <div class="threat-icon">⚠️</div>
          <div class="threat-details">
            <div class="threat-url">${truncateUrl(threat.url)}</div>
            <div class="threat-info">
              Threat Level: ${(threat.threatLevel * 100).toFixed(1)}%
              <span class="threat-time">${formatTime(threat.timestamp)}</span>
            </div>
          </div>
        </div>
      `)
      .join('');
    
    threatsList.innerHTML = threatsHtml;
  });
}

function truncateUrl(url) {
  const maxLength = 40;
  return url.length > maxLength ? url.substring(0, maxLength) + '...' : url;
}

function formatTime(timestamp) {
  const date = new Date(timestamp);
  return date.toLocaleString();
}

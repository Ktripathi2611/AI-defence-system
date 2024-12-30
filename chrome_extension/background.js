const API_URL = 'http://localhost:8000/api';

// Listen for navigation events
chrome.webNavigation.onBeforeNavigate.addListener(async (details) => {
  if (details.frameId === 0) { // Only check main frame
    try {
      const response = await fetch(`${API_URL}/threats/analyze/url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: details.url })
      });

      const result = await response.json();
      
      if (result.risk_score > 0.7) {
        // High risk - show warning notification
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon48.png',
          title: '⚠️ High Risk Website Detected',
          message: 'This website has been flagged as potentially dangerous. Proceed with caution.',
        });
      }
    } catch (error) {
      console.error('Error analyzing URL:', error);
    }
  }
});

// Listen for messages from content script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'SCAN_TEXT') {
    analyzeText(request.text)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ error: error.message }));
    return true; // Will respond asynchronously
  }
});

// Analyze text content
async function analyzeText(text) {
  try {
    const response = await fetch(`${API_URL}/spam/analyze/text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text: text })
    });
    return await response.json();
  } catch (error) {
    console.error('Error analyzing text:', error);
    throw error;
  }
}

// Listen for image analysis requests
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.type === 'ANALYZE_IMAGE') {
    analyzeImage(request.imageUrl)
      .then(result => sendResponse(result))
      .catch(error => sendResponse({ error: error.message }));
    return true;
  }
});

// Analyze images for potential deepfakes
async function analyzeImage(imageUrl) {
  try {
    const response = await fetch(`${API_URL}/deepfake/analyze/image`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: imageUrl })
    });
    return await response.json();
  } catch (error) {
    console.error('Error analyzing image:', error);
    throw error;
  }
}

// Initialize extension
chrome.runtime.onInstalled.addListener(() => {
  // Set default settings
  chrome.storage.sync.set({
    enableUrlCheck: true,
    enableTextAnalysis: true,
    enableImageAnalysis: true,
    notificationLevel: 'high' // 'high', 'medium', 'all'
  });
});

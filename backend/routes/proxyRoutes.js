const express = require('express');
const router = express.Router();
const axios = require('axios');

router.post('/proxy-request', async (req, res) => {
    const { url } = req.body;
    
    if (!url) {
        return res.status(400).json({ error: 'URL is required' });
    }

    try {
        const startTime = Date.now();
        const response = await axios({
            method: 'get',
            url: url,
            timeout: 10000,
            maxRedirects: 5,
            validateStatus: function (status) {
                return status >= 200 && status < 600;
            },
            headers: {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        });

        const responseTime = Date.now() - startTime;

        res.json({
            status: response.status,
            statusText: response.statusText,
            headers: response.headers,
            redirected: response.request.res.responseUrl !== url,
            redirectUrl: response.request.res.responseUrl,
            contentType: response.headers['content-type'],
            server: response.headers['server'],
            responseTime: responseTime,
            data: response.data
        });
    } catch (error) {
        console.error('Proxy request error:', error);
        
        if (error.response) {
            // Server responded with error status
            res.status(error.response.status).json({
                error: error.response.statusText,
                status: error.response.status,
                headers: error.response.headers
            });
        } else if (error.request) {
            // Request made but no response
            res.status(503).json({
                error: 'No response from server',
                details: error.message
            });
        } else {
            // Something else went wrong
            res.status(500).json({
                error: 'Failed to make request',
                details: error.message
            });
        }
    }
});

module.exports = router;

const express = require('express');
const request = require('request');
const cors = require('cors');

const app = express();
const PORT = 3002;

// Enable CORS for all routes
app.use(cors());
app.use('/proxy', (req, res) => {
    console.log(`Received request: ${req.method} ${req.url}`);

    // Remove the leading slash from req.url if it exists
    const cleanUrl = req.url.startsWith('/') ? req.url.slice(1) : req.url;
    
    // Construct the target URL
    const targetUrl = cleanUrl; // Replace with the actual target server URL
    console.log(`Forwarding request to: ${targetUrl}`); // Log the target URL

    const options = {
        method: req.method,
        url: targetUrl,
        headers: {
            ...req.headers,
            'host': 'api.backblaze.com',
        },
        body: req.body,
        json: true,
        agentOptions: {
            rejectUnauthorized: false // Disable SSL certificate validation
        }
    };
    
    const proxyRequest = request(options);
    
    req.pipe(proxyRequest).pipe(res);

    proxyRequest.on('error', (err) => {
        console.error('Error forwarding request:', err);
        res.status(500).send('Error forwarding request');
    });
});

app.listen(PORT, () => {
    console.log(`Proxy server running at http://localhost:${PORT}`);
});
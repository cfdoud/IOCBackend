const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const https = require('https');
const fs = require('fs');
const path = require('path');

const app = express();

// Load SSL certificates (adjust the path as needed)
const sslOptions = {
    key: fs.readFileSync(path.join(__dirname, 'server.key')),
    cert: fs.readFileSync(path.join(__dirname, 'server.cert'))
};

// Proxy configuration to forward requests to the camera stream
app.use('/camera_stream', createProxyMiddleware({
    target: 'http://192.168.1.254:8181',  // Camera's HTTP URL
    changeOrigin: true,
    pathRewrite: {
        '^/camera_stream': '/'  // Rewrite path to match the camera stream path
    }
}));

// Start HTTPS server
https.createServer(sslOptions, app).listen(3000, () => {
    console.log('Proxy server running at https://localhost:3000');
});

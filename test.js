const WebSocket = require('ws');
const http = require('http'); // HTTP for handling Raspberry Pi requests
const AWS = require('aws-sdk');
const fs = require('fs');
const path = require('path');
const os = require('os');
const https = require('https'); // HTTPS for WebSocket secure connections
require('dotenv').config({ path: './server.env' });

const port = 5001; // HTTPS port
const httpPort = 8080; // New HTTP port for Raspberry Pi requests

// HTTPS server for WebSocket connections
const httpsServer = https.createServer({
    cert: fs.readFileSync('/home/ubuntu/fullchain.pem'),
    key: fs.readFileSync('/home/ubuntu/privkey.pem'),
});

// HTTP server for Raspberry Pi requests
const httpServer = http.createServer((req, res) => {
    if (req.method === 'GET' && req.url === '/screenshot') {
        console.log('HTTP request received for screenshot');

        // Send a message to all WebSocket clients to take a screenshot
        const message = JSON.stringify({ type: 'pi-screenshot' });
        wss.clients.forEach(client => {
            if (client.readyState === WebSocket.OPEN) {
                client.send(message);
            }
        });

        // Respond to the HTTP request
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end('Screenshot command sent via WebSocket');
    } else {
        // Handle other routes if necessary
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
});

console.log("Keys loaded");
const wss = new WebSocket.Server({ server: httpsServer }); // WebSocket over HTTPS

// Function to get public IP
const getPublicIP = () => {
    return new Promise((resolve, reject) => {
        http.get('http://api.ipify.org', (resp) => {
            let data = '';
            resp.on('data', (chunk) => { data += chunk; });
            resp.on('end', () => { resolve(data); });
        }).on("error", (err) => { reject("Error fetching public IP: " + err.message); });
    });
};

// AWS SDK configuration
AWS.config.update({
    accessKeyId: process.env.AWS_ACCESS_KEY_ID,
    secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
    region: 'us-east-1'
});

const s3 = new AWS.S3();

// Function to delete an image from S3
const deleteImagefromS3 = (imageUrl) => {
    const key = imageUrl.split('/').pop();
    console.log('Deleting image from S3:', key);
    const deleteParams = {
        Bucket: process.env.AWS_BUCKET_NAME,
        Key: `temp/${key}`,
    };
    return s3.deleteObject(deleteParams).promise();
};

// Handle WebSocket connections
wss.on('connection', (ws) => {
    console.log('New client connected');

    ws.on('message', async (message) => {
        try {
            const parsedMessage = JSON.parse(message);
            console.log('Received message:', parsedMessage);

            // Handle screenshot uploads
            if (parsedMessage.type === "screenshot") {
                const base64Data = parsedMessage.data.replace(/^data:image\/png;base64,/, "");
                const now = new Date();
                const fileName = `screenshot-${now.toISOString().replace(/[:.]/g, '-')}.png`;
                const filePath = path.join(__dirname, fileName);
                fs.writeFileSync(filePath, base64Data, 'base64');

                uploadFile(filePath, fileName)
                    .then((data) => {
                        console.log(`File uploaded successfully: ${data.Location}`);
                        ws.send(JSON.stringify({ type: 'uploadSuccess', url: data.Location }));
                    })
                    .catch((err) => {
                        console.error("Error uploading file:", err);
                        ws.send(JSON.stringify({ type: 'uploadError', error: err.message }));
                    });
            } else if (parsedMessage.type === "delete") {
                const { imageUrl, id } = parsedMessage.data;

                if (typeof imageUrl !== 'string') {
                    console.error("Error: imageUrl is not a string:", imageUrl);
                    ws.send(JSON.stringify({ type: 'deleteError', error: 'imageUrl must be a string' }));
                    return;
                }

                try {
                    await deleteImagefromS3(imageUrl);
                    console.log('Image deleted from S3:', imageUrl);
                    ws.send(JSON.stringify({ type: 'deleteSuccess', id }));
                } catch (deleteError) {
                    console.error("Error deleting image:", deleteError);
                    ws.send(JSON.stringify({ type: 'deleteError', error: deleteError.message }));
                }
            } else {
                ws.send(JSON.stringify({ type: 'error', error: 'Invalid message type' }));
            }
        } catch (error) {
            ws.send(JSON.stringify({ type: 'error', error: 'Invalid message format' }));
        }
    });

    ws.on('close', () => {
        console.log('Client disconnected');
    });
});

// Start the HTTPS WebSocket server
httpsServer.listen(port, '0.0.0.0', async () => {
    const publicIP = await getPublicIP();
    console.log(`WebSocket server is running on wss://0.0.0.0:${port}`);
    console.log(`WebSocket server is accessible at wss://${publicIP}:${port}`);
});

// Start the HTTP server for Raspberry Pi
httpServer.listen(httpPort, '0.0.0.0', () => {
    console.log(`HTTP server is running on http://0.0.0.0:${httpPort}`);
});

// Function to upload a file to S3
const uploadFile = (filePath, fileName) => {
    const fileStream = fs.createReadStream(filePath);

    const uploadParams = {
        Bucket: process.env.AWS_BUCKET_NAME,
        Body: fileStream,
        Key: `temp/${fileName}`,
    };

    return s3.upload(uploadParams).promise()
        .then((data) => {
            fs.unlinkSync(filePath);
            return data;
        });
};

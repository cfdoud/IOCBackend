const WebSocket = require('ws');
const http = require('http'); // Import the http module
const AWS = require('aws-sdk');
const fs = require('fs');
const path = require('path');
const os = require('os');

require('dotenv').config({ path: './server.env' });
console.log("AWS_ACCESS_KEY_ID:", process.env.AWS_ACCESS_KEY_ID);
console.log("AWS_SECRET_ACCESS_KEY:", process.env.AWS_SECRET_ACCESS_KEY);
console.log("AWS_BUCKET_NAME:", process.env.AWS_BUCKET_NAME);

const port = 5001;
//const server = http.createServer(); // Create an HTTP server
const wss = new WebSocket.Server({ server }); // Pass the HTTP server to WebSocket
const server = https.createServer({
    cert: fs.readFileSync('/etc/letsencrypt/live/iocserver.paracontechnologies.com/fullchain.pem'),
    key: fs.readFileSync('/etc/letsencrypt/live/iocserver.paracontechnologies.com/privkey.pem'),
  });
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
    const key = imageUrl.split('/').pop(); // Ensure the key is correct
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
    
            // Defensive check for imageUrl
            if (typeof imageUrl !== 'string') {
              console.error("Error: imageUrl is not a string:", imageUrl);
              ws.send(JSON.stringify({ type: 'deleteError', error: 'imageUrl must be a string' }));
              return; // Exit the handler
            }
    
            try {
              await deleteImagefromS3(imageUrl); // Use imageUrl directly
              console.log('Image deleted from S3:', imageUrl);
              ws.send(JSON.stringify({ type: 'deleteSuccess', id }));
            } catch (deleteError) {
              console.error("Error deleting image:", deleteError);
              ws.send(JSON.stringify({ type: 'deleteError', error: deleteError.message }));
            }
          } else {
            console.log("Invalid message: Unknown message type.");
            ws.send(JSON.stringify({ type: 'error', error: 'Invalid message type' }));
          }
        } catch (error) {
          console.error("Error parsing message:", error);
          ws.send(JSON.stringify({ type: 'error', error: 'Invalid message format' }));
        }
      });
    
      ws.on('close', () => {
        console.log('Client disconnected');
      });
    });
    
// Handle HTTP requests
server.on('request', async (req, res) => {
    if (req.method === 'GET' && req.url === '/screenshot') {
      // Logic for handling screenshot trigger
      console.log('HTTP request received for screenshot');
      
      // Send a message to all WebSocket clients to take a screenshot
      const message = JSON.stringify({ type: 'pi-screenshot' }); // No data needed for trigger
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
  
  // Start the HTTP server
  server.listen(port, '0.0.0.0', async () => {
    const publicIP = await getPublicIP();
    console.log(`WebSocket server is running on ws://0.0.0.0:${port}`);
    console.log(`WebSocket server is accessible at ws://${publicIP}:${port}`);
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
      fs.unlinkSync(filePath); // Remove the file after upload
      return data;
    });
};

// Check for required environment variables
if (!process.env.AWS_BUCKET_NAME) {
  console.error("AWS_BUCKET_NAME environment variable is not set");
  process.exit(1);
}

console.log("Environment Variables Loaded:");
console.log("AWS_ACCESS_KEY_ID:", process.env.AWS_ACCESS_KEY_ID);
console.log("AWS_SECRET_ACCESS_KEY:", process.env.AWS_SECRET_ACCESS_KEY);
console.log("AWS_BUCKET_NAME:", process.env.AWS_BUCKET_NAME);

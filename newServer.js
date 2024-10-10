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
const server = http.createServer(); // Create an HTTP server
const wss = new WebSocket.Server({ server }); // Pass the HTTP server to WebSocket

// Print server address
console.log(`WebSocket server is running on ws://localhost:${port}`);
const interfaces = os.networkInterfaces();
for (const interface in interfaces) {
  for (const details of interfaces[interface]) {
    if (details.family === 'IPv4' && !details.internal) {
      console.log(`WebSocket server is accessible at ws://${details.address}:${port}`);
    }
  }
}

AWS.config.update({
  accessKeyId: process.env.AWS_ACCESS_KEY_ID, 
  secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY,
  region: 'us-east-1'
});

const s3 = new AWS.S3();

wss.on('connection', (ws) => {
  console.log('New client connected');

  ws.on('message', async (message) => {
    try {
      // Parse the incoming message as JSON
      const parsedMessage = JSON.parse(message);
      console.log('Received message:', parsedMessage);

      // Handle screenshot uploads
      if (parsedMessage.type === "screenshot") {
        const base64Data = parsedMessage.data.replace(/^data:image\/png;base64,/, "");
        
        // Name the image 
        const now = new Date();
        const fileName = `screenshot-${now.toISOString().replace(/[:.]/g, '-')}.png`;

        // Save the screenshot as a temporary file
        const filePath = path.join(__dirname, fileName);
        fs.writeFileSync(filePath, base64Data, 'base64');

        // Upload the file to S3
        uploadFile(filePath, fileName)
          .then((data) => {
            console.log(`File uploaded successfully: ${data.Location}`);
            ws.send(JSON.stringify({ type: 'uploadSuccess', url: data.Location }));
          })
          .catch((err) => {
            console.error("Error uploading file:", err);
            ws.send(JSON.stringify({ type: 'uploadError', error: err.message }));
          });
      } 
      // Handle image deletion
      else if (parsedMessage.type === "delete") {
        const { imageUrl, id } = parsedMessage.data;
    
        // Defensive check for imageUrl
        if (typeof imageUrl !== 'string') {
            console.error("Error: imageUrl is not a string:", imageUrl);
            ws.send(JSON.stringify({ type: 'deleteError', error: 'imageUrl must be a string' }));
            return; // Exit the handler
        }
    
        try {
            // Extracting the key from the URL for deletion
            const key = imageUrl.split('/').pop();
            await deleteImagefromS3(key);
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

  const deleteImagefromS3 = (imageUrl) => {
    const key = imageUrl.split('/').pop(); // Ensure the key is correct
    console.log('Deleting image from S3:', key);
    const deleteParams = {
      Bucket: process.env.AWS_BUCKET_NAME,
      Key: `temp/${key}`,
    };
   
    return s3.deleteObject(deleteParams).promise();
  };

  ws.on('close', () => {
    console.log('Client disconnected');
  });
});

// Handle HTTP requests
server.on('request', async (req, res) => {
  if (req.method === 'GET' && req.url === '/screenshot') {
    // Logic for handling screenshot trigger
    console.log('HTTP request received for screenshot');
    
    // Here you can implement the logic to trigger a screenshot
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
server.listen(port, () => {
  console.log(`HTTP server is running on http://localhost:${port}`);
});

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

if (!process.env.AWS_BUCKET_NAME) {
  console.error("AWS_BUCKET_NAME environment variable is not set");
  process.exit(1);
}

console.log("Environment Variables Loaded:");
console.log("AWS_ACCESS_KEY_ID:", process.env.AWS_ACCESS_KEY_ID);
console.log("AWS_SECRET_ACCESS_KEY:", process.env.AWS_SECRET_ACCESS_KEY);
console.log("AWS_BUCKET_NAME:", process.env.AWS_BUCKET_NAME);
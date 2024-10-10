const WebSocket = require('ws');
const fs = require("fs");
const HttpsServer = require('https').createServer;
const http = require('http');


class Client {
    constructor(websocket, clientType) {
        this.websocket = websocket;
        this.clientType = clientType;
    }
}

const server = HttpsServer({
    key: fs.readFileSync('/etc/letsencrypt/live/iocserver.paracontechnologies.com/privkey.pem'),
    cert: fs.readFileSync('/etc/letsencrypt/live/iocserver.paracontechnologies.com/fullchain.pem')
})

server.listen(5001);
console.log("Listening in port 5000.");

const websocketServer = new WebSocket.Server({ server: server });
const connectedClients = new Set();

function removeClient(client) {
    connectedClients.delete(client);
    console.log(`Client removed. Connected clients: ${connectedClients.size}`);
}


websocketServer.on('connection', (ws) => {
    let client;
    let rpiClient;

    ws.on('message', (message) => {
        if (!client) {
            // Assuming the first message is the client type
            client = new Client(ws, message.toString());
            connectedClients.add(client);
            
            if (client.clientType === "rpi") {
                rpiClient = client;
            }

            console.log(`${client.clientType} client connected.`);
            console.log(`Connected clients: ${connectedClients.size}`);

            ws.send('ready');
        } else {
            connectedClients.forEach((otherClient) => {
                if (otherClient.websocket !== ws && otherClient.websocket.readyState === WebSocket.OPEN) {
                    if (otherClient.clientType === "web") {
                        otherClient.websocket.send(message);
                    }

                    if (rpiClient && rpiClient.websocket.readyState === WebSocket.OPEN) {
                        rpiClient.websocket.send('ready');
                    }
                }
            });
        }
    });

    ws.on('close', () => {
        removeClient(client);
        console.log(`Disconnected. Connected Clients: ${connectedClients.size}`);
    });

    ws.on('error', (error) => {
        console.log('WebSocket error:', error);
        removeClient(client);
    });
});


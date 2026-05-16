require('dotenv').config({ path: '../../.env' });
const admin = require('firebase-admin');
const { Server } = require('@modelcontextprotocol/sdk/server/index.js');
const { SSEServerTransport } = require('@modelcontextprotocol/sdk/server/sse.js');
const express = require('express');

// Init Firebase
const serviceAccount = require(process.env.FIREBASE_CREDENTIALS_PATH || '../../firebase-credentials.json');
admin.initializeApp({ credential: admin.credential.cert(serviceAccount) });
const db = admin.firestore();

const server = new Server(
  { name: 'firebase-mcp', version: '1.0.0' },
  { capabilities: { tools: {} } }
);

// Tool: firestore_read
server.setRequestHandler('tools/call', async (request) => {
  const { name, arguments: args } = request.params;

  if (name === 'firestore_read') {
    const { collection, document } = args;
    const doc = await db.collection(collection).doc(document).get();
    return {
      content: [{ type: 'text', text: JSON.stringify(doc.exists ? doc.data() : null) }]
    };
  }

  if (name === 'firestore_write') {
    const { collection, document, data } = args;
    await db.collection(collection).doc(document).set(data, { merge: true });
    return {
      content: [{ type: 'text', text: JSON.stringify({ success: true, collection, document }) }]
    };
  }

  if (name === 'firestore_batch_write') {
    const { writes } = args; // array of { collection, document, data }
    const batch = db.batch();
    for (const write of writes) {
      const ref = db.collection(write.collection).doc(write.document);
      batch.set(ref, write.data, { merge: true });
    }
    await batch.commit();
    return {
      content: [{ type: 'text', text: JSON.stringify({ success: true, count: writes.length }) }]
    };
  }

  if (name === 'firestore_listen') {
    // Returns current state — Antigravity polls rather than uses real-time listeners
    const { collection } = args;
    const snapshot = await db.collection(collection).get();
    const docs = snapshot.docs.map(d => ({ id: d.id, ...d.data() }));
    return {
      content: [{ type: 'text', text: JSON.stringify(docs) }]
    };
  }

  throw new Error(`Unknown tool: ${name}`);
});

// List available tools
server.setRequestHandler('tools/list', async () => ({
  tools: [
    { name: 'firestore_read', description: 'Read a Firestore document', inputSchema: { type: 'object', properties: { collection: { type: 'string' }, document: { type: 'string' } }, required: ['collection', 'document'] } },
    { name: 'firestore_write', description: 'Write to a Firestore document', inputSchema: { type: 'object', properties: { collection: { type: 'string' }, document: { type: 'string' }, data: { type: 'object' } }, required: ['collection', 'document', 'data'] } },
    { name: 'firestore_batch_write', description: 'Write multiple Firestore documents', inputSchema: { type: 'object', properties: { writes: { type: 'array' } }, required: ['writes'] } },
    { name: 'firestore_listen', description: 'Get all documents in a collection', inputSchema: { type: 'object', properties: { collection: { type: 'string' } }, required: ['collection'] } }
  ]
}));

// SSE transport for Antigravity
const app = express();
app.get('/sse', async (req, res) => {
  const transport = new SSEServerTransport('/messages', res);
  await server.connect(transport);
});
app.post('/messages', express.json(), async (req, res) => {
  res.json({ status: 'ok' });
});

const PORT = process.env.MCP_PORT || 3001;
app.listen(PORT, () => console.log(`Axion Firebase MCP server running on port ${PORT}`));

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Submit article — backend writes to Firestore, Antigravity takes over
export async function analyzeArticle(inputType, content) {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ input_type: inputType, content })
  });
  return res.json(); // returns { run_id, status: "queued" }
}

// Poll until Antigravity pipeline is complete
export async function pollStatus(runId, onUpdate, maxWaitMs = 60000) {
  const start = Date.now();
  while (Date.now() - start < maxWaitMs) {
    const res = await fetch(`${API_BASE}/status/${runId}`);
    const data = await res.json();
    onUpdate(data);
    if (data.status === 'complete') return true;
    await new Promise(r => setTimeout(r, 2000)); // poll every 2 seconds
  }
  return false;
}

// Fetch final report assembled by ComposerAgent
export async function getFinalReport() {
  const res = await fetch(`${API_BASE}/report`);
  return res.json();
}

// Reset Firestore to before-state (for demo reset)
export async function resetState() {
  const res = await fetch(`${API_BASE}/seed`, { method: 'POST' });
  return res.json();
}

// Run demo with hardcoded SBP article
export async function runDemo() {
  return analyzeArticle('demo', '');
}

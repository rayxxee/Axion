# Axion — Technical Architecture Document

## 1. System Overview

Axion is an autonomous content-to-action agent system built for Challenge 1 of the Google Antigravity Hackathon 2026. It processes unstructured Pakistani financial news and translates it into concrete, simulated business actions for a logistics company.

### Core Innovation
**Zero-backend-intelligence architecture.** Unlike traditional agent systems where a backend orchestrates LLM calls, Axion's backend is a pure trigger layer. All reasoning, analysis, strategy generation, and simulation execution happens inside Antigravity agents. Firebase Firestore serves as the shared state bus, and a custom MCP server bridges Antigravity with Firestore.

---

## 2. Architecture Layers

### Layer 1: Input Layer (Flutter + React)
- **Flutter Mobile App** (`flutter_app/`): 3-screen app (Input → Processing → Result)
  - Accepts text paste, URL input, PDF upload, or demo article
  - POSTs to FastAPI backend
  - Polls `pipeline_status` for completion
  - Renders full report with before/after pricing, notifications, alerts
- **React Dashboard** (`dashboard/`): Vite-powered SPA
  - 9 components: InsightCard, ImpactMetrics, ActionList, BeforeAfterTable, ExecutionLog, NotificationPreview, PipelineProgress, ArticleInput, Sidebar
  - 3 pages: AnalyzePage, ResultsPage, HistoryPage
  - Polls backend API for real-time updates

### Layer 2: Trigger Layer (FastAPI)
The backend has exactly 7 endpoints and makes **zero LLM calls**:

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Health check |
| `/analyze` | POST | Accept text/URL/demo article, write to Firestore |
| `/analyze/pdf` | POST | Accept PDF upload, extract text, write to Firestore |
| `/status/{run_id}` | GET | Return current pipeline status |
| `/report` | GET | Return final assembled report |
| `/history` | GET | Return past analysis entries |
| `/trace` | GET | Return execution log entries |
| `/seed` | POST | Reset pricing table to baseline |

Supporting services:
- `news_ingester.py`: URL → text via httpx + BeautifulSoup
- `pdf_extractor.py`: PDF bytes → text via PyMuPDF (fitz)
- `firebase_client.py`: Firestore CRUD helpers with async wrappers

### Layer 3: State Bus (Firebase Firestore)
9 collections forming the inter-agent communication backbone:

```
pending_analysis     ← Frontend writes, AnalystAgent reads
agent_outputs        ← Each agent writes its result here (agent1_result...agent4_result)
pricing_table        ← Seed data + mutated by ExecutorAgent
simulation_state     ← before/after pricing snapshots
notification_drafts  ← Email + SMS templates from ExecutorAgent
workflow_alerts      ← Stakeholder alerts from ExecutorAgent
execution_log        ← Timestamped agent activity log
final_report         ← Assembled output for frontends
pipeline_status      ← Completion signal
```

### Layer 4: Intelligence Layer (Antigravity Agents)
5 sequential agents orchestrated via Antigravity Manager View across 3 workspaces:

```
Workspace A: AnalystAgent → ImpactAgent     (sequential)
Workspace B: StrategyAgent                  (waits for A)
Workspace C: ExecutorAgent → ComposerAgent  (sequential, waits for B)
```

### Layer 5: Bridge Layer (MCP Server)
Custom Node.js Express server implementing Model Context Protocol:
- Transport: Server-Sent Events (SSE) on port 3001
- 4 tools exposed: `firestore_read`, `firestore_write`, `firestore_batch_write`, `firestore_listen`
- Session management via `SSEServerTransport` with cleanup on disconnect

---

## 3. Agent Pipeline Detail

### Sequential Trigger Chain
```
User submits article
  → Backend writes to pending_analysis
    → AnalystAgent reads, extracts facts, writes agent1_result
      → ImpactAgent reads agent1_result, calculates PKR impact, writes agent2_result
        → StrategyAgent reads agent2_result, generates 3 ranked actions, writes agent3_result
          → ExecutorAgent reads agent3_result + agent2_result, runs 3 simulations:
            1. Updates pricing_table (before→after)
            2. Drafts email + SMS notifications (with Urdu)
            3. Creates P1 stakeholder alert with escalation path
            → Writes agent4_result
              → ComposerAgent reads ALL outputs, assembles final_report
                → Sets pipeline_status = "complete"
                  → Frontends detect completion, render results
```

### Model Selection Rationale
| Agent | Model | Rationale |
|---|---|---|
| AnalystAgent | Gemini 3.1 Flash Lite | Pure extraction, no reasoning needed, lowest cost |
| ImpactAgent | Gemini 3 Flash | Business arithmetic + moderate reasoning |
| StrategyAgent | Claude Sonnet 4 | Critical strategic reasoning requires strongest model |
| ExecutorAgent | Gemini 3 Flash | Template generation + structured Firestore writes |
| ComposerAgent | Claude Haiku 4.5 | JSON assembly discipline, cheapest Claude |

---

## 4. Simulation Architecture

The ExecutorAgent runs 3 sub-simulations for the Rank 1 action:

### Simulation 1: Pricing Update
- Reads current `pricing_table` (5 products)
- Saves snapshot to `simulation_state/before`
- Applies `breakeven_price_increase_pct` from ImpactAgent
- Rounds to nearest Rs. 5
- Flags products with >15% increase as `requires_approval: true`
- Writes updated prices to `pricing_table`
- Saves snapshot to `simulation_state/after`

### Simulation 2: Notification Draft
- Generates professional email (150-200 words, empathetic tone)
- Generates SMS (≤160 chars, includes one Urdu word naturally)
- Creates internal operations alert
- Writes to `notification_drafts` collection

### Simulation 3: Workflow Alert
- Creates priority-based alert (P1/P2/P3 based on severity)
- Defines required actions per team with deadlines
- Sets escalation path (operations_manager → finance_lead → CEO)
- Writes to `workflow_alerts` collection

---

## 5. Security

### Firestore Rules
- Read/write restricted by collection
- `pricing_table`, `agent_outputs`, `simulation_state`: read-write for authenticated clients
- `execution_log`: append-only pattern
- Production deployment would require Firebase Auth integration

### Environment Security
- API keys stored in `.env` (gitignored)
- Firebase credentials via service account JSON (gitignored)
- CORS configured to allow all origins (development mode)

---

## 6. Mock vs Real APIs

| Component | Mock/Real | Details |
|---|---|---|
| News text extraction (URL) | Real | Live HTTP fetch + HTML parsing |
| PDF text extraction | Real | Binary PDF → text via PyMuPDF |
| LLM reasoning (all agents) | Real | Live API calls via Antigravity |
| Firestore read/write | Real | Live Firebase Firestore |
| Pricing table data | Mock | Hardcoded 5-product seed data |
| Notification sending | Mock | Drafts generated but not dispatched |
| Stakeholder alerts | Mock | Written to Firestore but not sent externally |
| Business profile | Mock | Fixed parameters (Lahore logistics, 200 orders/day) |

---

*Built for Google Antigravity Hackathon 2026*

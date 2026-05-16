# Axion — Antigravity-Orchestrated News Impact Pipeline

A 5-agent AI pipeline that ingests news articles, analyzes PKR business impact, generates ranked actions, and simulates execution with before/after state — **fully orchestrated by Google Antigravity**.

## Architecture

```
Flutter/React → POST /analyze → Backend writes to Firestore
                                     ↓
                          Antigravity agents pick it up
                                     ↓
              AnalystAgent → ImpactAgent → StrategyAgent → ExecutorAgent → ComposerAgent
                                     ↓
                   Results written to Firestore → Flutter/React displays
```

| Component | Stack |
|---|---|
| **Orchestrator** | Google Antigravity (Manager View) |
| **Agent Definitions** | `.agents/` markdown files |
| **Backend** | FastAPI — thin trigger layer, zero LLM calls |
| **Database** | Firebase Firestore (shared state bus) |
| **MCP Bridge** | Express-based Firebase MCP server (port 3001) |
| **Web Dashboard** | React + Tailwind CSS |
| **Models** | Claude Sonnet 4.6 · Claude Haiku 4.5 · Gemini 3 Flash · Gemini 3.1 Flash-Lite |

## Agent Pipeline

| # | Agent | Model | Role |
|---|---|---|---|
| 1 | AnalystAgent | gemini-3.1-flash-lite | Extract economic signals from news |
| 2 | ImpactAgent | gemini-3-flash | Calculate PKR business impact |
| 3 | StrategyAgent | claude-sonnet-4-6 | Generate 3 ranked business actions |
| 4 | ExecutorAgent | gemini-3-flash | Run 3 simulations (pricing, notifications, alerts) |
| 5 | ComposerAgent | claude-haiku-4-5 | Assemble final report |

## Prerequisites

- Python 3.11+
- Node.js 18+
- Firebase project with Firestore enabled
- Firebase service account JSON credentials
- Anthropic API key (for Claude agents)
- Gemini API key (for Gemini agents)

## Setup

### 1. Environment

```bash
cp .env.example .env
# Fill in ALL keys in .env:
#   ANTHROPIC_API_KEY, GEMINI_API_KEY,
#   FIREBASE_PROJECT_ID, FIREBASE_CREDENTIALS_PATH
```

### 2. Firebase MCP Server

```bash
cd firebase/mcp_server
npm install
node index.js
# Must be running on port 3001 before opening Antigravity
```

### 3. Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 4. Seed Firestore (first run)

```bash
# From backend/ directory:
python -c "import asyncio; from services.firebase_client import seed_pricing_table; asyncio.run(seed_pricing_table())"
# Or hit the endpoint:
curl -X POST http://localhost:8000/seed
```

### 5. Dashboard

```bash
cd dashboard
npm install
npm run dev
```

### 6. Antigravity (Agent Orchestration)

1. Open Axion project in Antigravity
2. Confirm `mcp.json` is detected (MCP panel → firebase-mcp connected)
3. Open **Manager View** → create 3 workspaces:
   - **Workspace A**: `01_analyst_agent.md` + `02_impact_agent.md`
   - **Workspace B**: `03_strategy_agent.md`
   - **Workspace C**: `04_executor_agent.md` + `05_composer_agent.md`
4. Set each workspace's model per `pipeline_config.md`

## API Endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Health check (returns version + architecture) |
| POST | `/analyze` | Submit article → Firestore → Antigravity takes over |
| GET | `/status/{run_id}` | Poll pipeline status until complete |
| GET | `/report` | Fetch final assembled report |
| POST | `/seed` | Reset Firestore pricing table to baseline |

## Demo Inputs

- `"SBP raises interest rate by 200bps"`
- `"Petrol price increased by 18%"`
- `"PKR depreciates 3% against USD"`

## Testing Without Antigravity

The backend can be tested standalone — it writes to Firestore and exposes polling endpoints. Agents must be triggered manually via Antigravity Manager View or by writing mock data directly to Firestore `agent_outputs` collection.

```bash
# Health check
curl http://localhost:8000/health

# Seed pricing table
curl -X POST http://localhost:8000/seed

# Submit demo article
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"input_type": "demo", "content": ""}'

# Check status
curl http://localhost:8000/status/<run_id>
```

## Firestore Collections

| Collection | Purpose |
|---|---|
| `pending_analysis` | Input articles from Flutter/React |
| `agent_outputs` | agent1_result through agent4_result |
| `pricing_table` | Product pricing (mutated by ExecutorAgent) |
| `simulation_state` | Before/after snapshots |
| `notification_drafts` | Email + SMS output |
| `workflow_alerts` | Stakeholder alert output |
| `execution_log` | Timestamped log entries from all agents |
| `final_report` | Assembled output (read by clients) |
| `pipeline_status` | Completion signal polled by clients |

## Export Agent Trace

```bash
python scripts/export_agent_trace.py
# Exports execution_log from Firestore → agent_trace.json
```

---

*Axion v2.0 — Antigravity-Orchestrated Architecture*
*Stack: Google Antigravity · Claude Sonnet 4.6 · Claude Haiku 4.5 · Gemini 3 Flash · Gemini 3.1 Flash-Lite · Firebase Firestore MCP · React*

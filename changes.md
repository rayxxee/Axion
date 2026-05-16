# Axion — Antigravity Refactoring Master Prompt

## Read this entire file before touching a single line of code

> **You are refactoring the Axion repository (github.com/rayxxee/Axion) from a FastAPI-centric agent system into an Antigravity-orchestrated agentic pipeline.**
> The intelligence must move OUT of Python functions and INTO Antigravity agents.
> The backend becomes a thin trigger layer only.
> Firebase Firestore becomes the shared state bus between Antigravity and the frontend.

---

## 0. Current State of the Repo (what exists today)

```
Axion/
├── .agents/              ← exists but currently unused properly
├── backend/              ← FastAPI app, ALL agent logic lives here as Python functions
├── dashboard/            ← React + Tailwind web dashboard
├── firebase/             ← Firebase config/setup
├── scripts/              ← utility scripts
├── .env.example          ← ANTHROPIC_API_KEY, NEWS_API_KEY, FIREBASE_PROJECT_ID, FIREBASE_CREDENTIALS_PATH
├── .gitignore
└── README.md
```

**Current architecture (WRONG for this challenge):**

```
Flutter → FastAPI → Python calls Claude API directly → returns JSON → Flutter displays it
Antigravity = just helped write the code, not part of runtime
```

**Target architecture (CORRECT for this challenge):**

```
Flutter → writes article to Firestore → Antigravity agents pick it up
Antigravity agents reason → execute → write results back to Firestore
Flutter reads results from Firestore → displays before/after dashboard
Antigravity generates trace logs → submitted as proof of autonomy
```

---

## 1. What Must Change — The Non-Negotiables

### 1.1 Agent logic leaves Python entirely

Every `agents/` file in the backend that calls Claude/Gemini and does reasoning **must be gutted**. Replace the body of each agent function with a single Firestore write that triggers the corresponding Antigravity agent. The Python files become webhooks/triggers, not thinkers.

### 1.2 `.agents/` folder becomes the real agent definitions

The `.agents/` folder must contain one markdown file per agent. These are the actual agent instruction files that Antigravity reads. This is where ALL reasoning prompts live from now on.

### 1.3 Gemini API key added to .env

Current `.env.example` only has `ANTHROPIC_API_KEY`. We are now using a mixed model stack. Add `GEMINI_API_KEY`.

### 1.4 MCP config added

Antigravity agents connect to Firestore via MCP. A new `mcp.json` config file must be created.

### 1.5 Backend shrinks to 3 responsibilities only

1. Receive article input from Flutter (POST /analyze)
2. Write it to Firestore `pending_analysis` collection
3. Seed the pricing table on startup (GET /seed)

That is ALL the backend does. No LLM calls. No agent logic. No chaining.

---

## 2. New Repository Structure (refactored)

```
Axion/
│
├── .agents/                          ← ANTIGRAVITY AGENT DEFINITIONS (the brain)
│   ├── 01_analyst_agent.md           ← Agent 1: news extraction
│   ├── 02_impact_agent.md            ← Agent 2: PKR business impact calculation
│   ├── 03_strategy_agent.md          ← Agent 3: ranked action generation
│   ├── 04_executor_agent.md          ← Agent 4: orchestrates 3 simulations
│   ├── 04a_pricing_updater.md        ← Sub-agent 4a: Firestore pricing write
│   ├── 04b_notif_drafter.md          ← Sub-agent 4b: email + SMS generation
│   ├── 04c_workflow_trigger.md       ← Sub-agent 4c: stakeholder alert JSON
│   ├── 05_composer_agent.md          ← Agent 5: final report assembly
│   └── pipeline_config.md            ← pipeline order, triggers, model assignments
│
├── backend/                          ← THIN TRIGGER LAYER ONLY (no LLM calls)
│   ├── main.py                       ← 3 endpoints only: /analyze, /seed, /health
│   ├── requirements.txt              ← remove anthropic SDK, keep firebase-admin + fastapi
│   └── services/
│       ├── firebase_client.py        ← Firestore read/write helpers
│       └── news_ingester.py          ← URL scraping (BeautifulSoup) — keep this
│
├── dashboard/                        ← React dashboard (mostly unchanged, rewire data source)
│   └── src/
│       ├── services/api.js           ← change: poll Firestore directly, not FastAPI agents
│       └── components/               ← keep all existing components
│
├── firebase/
│   ├── firestore.rules               ← Firestore security rules
│   ├── seed_data.json                ← 5 PKR product records (before state)
│   └── mcp_server/                   ← NEW: Firebase MCP server for Antigravity
│       ├── index.js
│       └── package.json
│
├── scripts/
│   ├── seed_firestore.py             ← seeds pricing_table collection
│   └── export_agent_trace.py         ← NEW: exports Antigravity logs for submission
│
├── mcp.json                          ← NEW: MCP configuration for Antigravity
├── .env.example                      ← updated: add GEMINI_API_KEY
├── .gitignore
└── README.md                         ← update architecture section
```

---

## 3. The `.agents/` Files — Write These Exactly

### `01_analyst_agent.md`

```markdown
# Analyst Agent

**Model:** gemini-3.1-flash-lite
**Trigger:** New document appears in Firestore collection `pending_analysis`
**MCP Tools:** firestore_read, firestore_write

## Instructions

You are a precision news extraction engine for the Axion pipeline.

When triggered, do the following steps in order:

**Step 1:** Read the document from Firestore collection `pending_analysis`.
Extract the field `article_text`.

**Step 2:** Extract ONLY verifiable facts from the article. No interpretation.
No inference. No opinions. No summaries.

**Step 3:** Produce this exact JSON structure:
{
  "headline": "exact headline or first sentence of article",
  "date": "YYYY-MM-DD or null",
  "topic": "monetary_policy|fuel_prices|taxation|trade|inflation|exchange_rate|other",
  "key_entities": ["list of organizations, people, policies mentioned"],
  "economic_signals": [
    {
      "signal": "plain description of the economic fact",
      "magnitude": "exact number with unit e.g. 200bps, 18%, Rs.50/litre",
      "direction": "up|down|neutral"
    }
  ],
  "source_credibility_score": 0.0
}

source_credibility_score scale:
- 0.9 to 1.0 = official government or SBP source
- 0.7 to 0.89 = major news outlet (Dawn, Geo, ARY, Tribune)
- 0.5 to 0.69 = blog or unknown outlet
- 0.0 to 0.49 = unverified

**Step 4:** Write your JSON output to Firestore:
- Collection: `agent_outputs`
- Document: `agent1_result`
- Field: `data` (your JSON), `completed_at` (ISO timestamp), `status` "complete"

**Step 5:** Append to Firestore collection `execution_log`:
{
  "agent": "AnalystAgent",
  "action": "Extracted economic signals from article",
  "output_preview": "first economic signal description",
  "status": "success",
  "timestamp": "HH:MM:SS"
}

Return only valid JSON in Step 3. No markdown fences. No explanation text.
```

---

### `02_impact_agent.md`

```markdown
# Impact Agent

**Model:** gemini-3-flash
**Trigger:** Document `agent1_result` appears in Firestore `agent_outputs` with status "complete"
**MCP Tools:** firestore_read, firestore_write

## Instructions

You are a Pakistan business impact analyst for the Axion pipeline.

**Step 1:** Read `agent_outputs/agent1_result` from Firestore. Extract the `data` field.

**Step 2:** Use these fixed business parameters for ALL calculations:
- Company type: Mid-size distribution company, Lahore HQ
- Daily orders: 200 orders per day
- Average order value: Rs. 3,500
- Base delivery cost: Rs. 180 per order
- Fuel component of delivery cost: 35% (Rs. 63 per order)
- Current average margin: 18%
- Monthly revenue: Rs. 21,000,000

**Step 3:** Calculate the REAL business consequences of each economic signal.
Show your arithmetic. Be specific. Use PKR amounts, not vague language.

**Step 4:** Produce this exact JSON structure:
{
  "impact_summary": "2 sentences maximum, plain English, must include PKR figures",
  "affected_sectors": ["logistics", "procurement", "pricing", etc.],
  "quantified_metrics": {
    "delivery_cost_change_pkr": number (per order, positive means increase),
    "delivery_cost_change_pct": number,
    "margin_change_pct": number (negative means compression),
    "affected_orders_per_day": number,
    "monthly_revenue_impact_pkr": number (negative means loss),
    "breakeven_price_increase_pct": number
  },
  "severity": "low|medium|high|critical",
  "severity_rationale": "one sentence with the key number driving this severity rating"
}

Severity thresholds:
- low: margin change less than 2%
- medium: margin change 2% to 5%
- high: margin change 5% to 10%
- critical: margin change greater than 10%

**Step 5:** Write output to `agent_outputs/agent2_result` with status "complete".

**Step 6:** Append to `execution_log`:
{
  "agent": "ImpactAgent",
  "action": "Calculated PKR business impact",
  "output_preview": "severity level + monthly impact amount",
  "status": "success",
  "timestamp": "HH:MM:SS"
}
```

---

### `03_strategy_agent.md`

```markdown
# Strategy Agent

**Model:** claude-sonnet-4-6
**Trigger:** Document `agent2_result` appears in Firestore `agent_outputs` with status "complete"
**MCP Tools:** firestore_read, firestore_write

## Instructions

You are a senior Pakistan business strategy advisor for the Axion pipeline.

**Step 1:** Read `agent_outputs/agent2_result` from Firestore. Extract the `data` field.

**Step 2:** Generate exactly 3 ranked, executable business actions.

Rules for actions:
- Must be specific to Pakistan market (mention PKR figures, SBP regulations, Lahore logistics)
- Must be immediately actionable within 1 to 2 weeks
- Rank 1 = most urgent, highest business impact
- Only Rank 1 has simulate set to true
- Ranks 2 and 3 have simulate set to false

**Step 3:** Produce this exact JSON structure:
{
  "actions": [
    {
      "rank": 1,
      "title": "action title maximum 8 words",
      "rationale": "why this action, directly linked to quantified impact numbers from agent2",
      "steps": [
        "Specific executable step 1",
        "Specific executable step 2",
        "Specific executable step 3"
      ],
      "expected_outcome": "quantified outcome e.g. recover Rs. X margin per order",
      "effort": "low|medium|high",
      "impact": "low|medium|high",
      "timeframe": "immediate|1_week|2_weeks|1_month",
      "simulate": true
    },
    {
      "rank": 2,
      "title": "...",
      "rationale": "...",
      "steps": ["...", "...", "..."],
      "expected_outcome": "...",
      "effort": "low|medium|high",
      "impact": "low|medium|high",
      "timeframe": "...",
      "simulate": false
    },
    {
      "rank": 3,
      "title": "...",
      "rationale": "...",
      "steps": ["...", "...", "..."],
      "expected_outcome": "...",
      "effort": "low|medium|high",
      "impact": "low|medium|high",
      "timeframe": "...",
      "simulate": false
    }
  ],
  "decision_rationale": "one sentence explaining why rank 1 was prioritized over alternatives"
}

**Step 4:** Write output to `agent_outputs/agent3_result` with status "complete".

**Step 5:** Append to `execution_log`:
{
  "agent": "StrategyAgent",
  "action": "Generated 3 ranked Pakistan-specific business actions",
  "output_preview": "Rank 1 action title",
  "status": "success",
  "timestamp": "HH:MM:SS"
}
```

---

### `04_executor_agent.md`

```markdown
# Executor Agent

**Model:** gemini-3-flash
**Trigger:** Document `agent3_result` appears in Firestore `agent_outputs` with status "complete"
**MCP Tools:** firestore_read, firestore_write, firestore_batch_write

## Instructions

You are the execution agent for the Axion pipeline. Your job is to simulate
the Rank 1 action by running 3 sub-simulations.

**Step 1:** Read `agent_outputs/agent3_result` and `agent_outputs/agent2_result` from Firestore.

**Step 2:** Read the current `pricing_table` collection from Firestore.
Save this as the BEFORE STATE. Write it to `simulation_state/before` immediately.

**Step 3:** Run all 3 simulations. Treat them as parallel tasks.

--- SIMULATION 1: Pricing Update ---
Using the quantified_metrics from agent2_result, calculate new prices for
every product in pricing_table.

Calculation rules:
- Apply the breakeven_price_increase_pct to maintain 18% margin
- Round every new price to the nearest Rs. 5
- Flag products where new price exceeds 15% increase as requires_approval: true

Write updated prices back to `pricing_table` collection (overwrite each document).
Write the updated table to `simulation_state/after`.

--- SIMULATION 2: Notification Draft ---
Write to Firestore collection `notification_drafts` a new document containing:
{
  "email": {
    "subject": "clear subject line about the pricing change",
    "body": "professional email body 150-200 words, acknowledge external factor, empathetic tone",
    "recipients_type": "customers"
  },
  "sms": {
    "body": "MAXIMUM 160 characters including spaces, include one Urdu word naturally",
    "character_count": number
  },
  "internal_alert": "2-3 lines, terse, action-oriented for the operations team"
}

--- SIMULATION 3: Workflow Alert ---
Write to Firestore collection `workflow_alerts` a new document containing:
{
  "alert_id": "generate a uuid",
  "priority": "P1|P2|P3 based on severity from agent2",
  "category": "pricing|operations|finance|procurement",
  "title": "alert title",
  "description": "alert description",
  "triggered_by": "Axion Agent Pipeline",
  "news_headline": "from agent1_result",
  "impact_severity": "from agent2_result",
  "required_actions": [
    {
      "team": "finance|operations|management|sales",
      "action": "specific action required",
      "deadline": "24h|48h|1_week"
    }
  ],
  "escalation_path": ["operations_manager", "finance_lead", "ceo"],
  "created_at": "ISO8601 timestamp"
}

**Step 4:** Write execution summary to `agent_outputs/agent4_result` with status "complete".

**Step 5:** Append 3 entries to `execution_log` — one per simulation:
- Entry 1: agent "ExecutorAgent:PricingUpdater", action "Updated pricing_table in Firestore"
- Entry 2: agent "ExecutorAgent:NotifDrafter", action "Generated email and SMS drafts"
- Entry 3: agent "ExecutorAgent:WorkflowTrigger", action "Created P1 stakeholder alert"
All with status "success" and individual timestamps.
```

---

### `05_composer_agent.md`

```markdown
# Composer Agent

**Model:** claude-haiku-4-5-20251001
**Trigger:** Document `agent4_result` appears in Firestore `agent_outputs` with status "complete"
**MCP Tools:** firestore_read, firestore_write

## Instructions

You are the output composer for the Axion pipeline. You do NOT add new analysis.
You only organize, connect, and structure what all previous agents produced.

**Step 1:** Read ALL of the following from Firestore:
- `agent_outputs/agent1_result`
- `agent_outputs/agent2_result`
- `agent_outputs/agent3_result`
- `agent_outputs/agent4_result`
- `simulation_state/before`
- `simulation_state/after`
- All documents in `execution_log` collection (ordered by timestamp)
- `notification_drafts` (most recent document)
- `workflow_alerts` (most recent document)

**Step 2:** Format ALL PKR amounts as "Rs. X,XXX" with comma separators.

**Step 3:** Assemble and write the final report to Firestore document `final_report`:
{
  "insight_card": {
    "headline": "from agent1_result",
    "one_line_insight": "single most important finding in plain English",
    "severity": "from agent2_result",
    "severity_color": "green|yellow|orange|red",
    "key_metrics": [
      "Rs. X increase per delivery",
      "X% margin compression",
      "Rs. X,XXX monthly impact"
    ]
  },
  "pipeline_summary": {
    "total_agents_run": 5,
    "total_processing_time_ms": number,
    "actions_generated": 3,
    "simulations_executed": 3
  },
  "impact_metrics": {
    "delivery_cost_change_pkr": "Rs. X formatted",
    "margin_change_pct": number,
    "monthly_revenue_impact_pkr": "Rs. X,XXX formatted",
    "affected_orders_per_day": number
  },
  "actions": "full actions array from agent3_result",
  "notification_draft": "full object from notification_drafts",
  "workflow_alert": "full object from workflow_alerts",
  "execution_log": "all entries from execution_log collection",
  "before_state": "pricing_table array from simulation_state/before",
  "after_state": "pricing_table array from simulation_state/after",
  "state_change_summary": "one sentence: X products repriced, average increase Y%, effective immediately"
}

**Step 4:** Write to Firestore document `pipeline_status`:
{
  "status": "complete",
  "completed_at": "ISO8601 timestamp",
  "run_id": "same run_id from pending_analysis trigger"
}

This `pipeline_status` document is what the Flutter app polls to know when to display results.

**Step 5:** Append final entry to `execution_log`:
{
  "agent": "ComposerAgent",
  "action": "Assembled final report — pipeline complete",
  "output_preview": "state_change_summary value",
  "status": "success",
  "timestamp": "HH:MM:SS"
}
```

---

### `pipeline_config.md`

```markdown
# Axion Pipeline Configuration

## Model Assignments
| Agent | Model | Reason |
|---|---|---|
| AnalystAgent | gemini-3.1-flash-lite | Pure extraction, no reasoning, cheapest |
| ImpactAgent | gemini-3-flash | Business math + some reasoning, Pro-grade at Flash cost |
| StrategyAgent | claude-sonnet-4-6 | Critical strategic reasoning — keep Claude |
| ExecutorAgent | gemini-3-flash | Template generation + structured writes |
| ComposerAgent | claude-haiku-4-5-20251001 | JSON assembly discipline, cheapest Claude |

## Trigger Chain (sequential)
1. Flutter writes to `pending_analysis` → triggers AnalystAgent
2. `agent1_result` status="complete" → triggers ImpactAgent
3. `agent2_result` status="complete" → triggers StrategyAgent
4. `agent3_result` status="complete" → triggers ExecutorAgent
5. `agent4_result` status="complete" → triggers ComposerAgent
6. `pipeline_status` status="complete" → Flutter app displays results

## Firestore Collections Used
- `pending_analysis` — input from Flutter
- `agent_outputs` — agent1_result through agent4_result
- `pricing_table` — product pricing (mutated by ExecutorAgent)
- `simulation_state` — before and after snapshots
- `notification_drafts` — email + SMS output
- `workflow_alerts` — stakeholder alert output
- `execution_log` — timestamped log entries from all agents
- `final_report` — assembled output (read by Flutter + React)
- `pipeline_status` — completion signal polled by Flutter

## Manager View Workspace Layout
- Workspace A: AnalystAgent + ImpactAgent (sequential)
- Workspace B: StrategyAgent (waits for Workspace A)
- Workspace C: ExecutorAgent + ComposerAgent (sequential, waits for B)
```

---

## 4. Refactored Backend — Replace Existing Files

### `backend/main.py` — REPLACE ENTIRELY

```python
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from services.firebase_client import (
    write_pending_analysis,
    seed_pricing_table,
    get_pipeline_status,
    get_final_report
)
from services.news_ingester import fetch_article_from_url
import uuid
from datetime import datetime

app = FastAPI(title="Axion API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    input_type: str   # "text" | "url" | "demo"
    content: str      # raw text or URL

DEMO_INPUT = """SBP has raised the policy rate by 200 basis points to 22%,
effective immediately. This is the third consecutive hike aimed at controlling
inflation which stands at 28% YoY."""

@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.0.0", "architecture": "antigravity-orchestrated"}

@app.post("/analyze")
async def analyze(request: AnalyzeRequest):
    """
    Receives article from Flutter.
    Writes it to Firestore pending_analysis.
    Antigravity agents take over from here.
    """
    run_id = str(uuid.uuid4())

    if request.input_type == "demo":
        article_text = DEMO_INPUT
    elif request.input_type == "url":
        article_text = await fetch_article_from_url(request.content)
        if not article_text:
            raise HTTPException(status_code=400, detail="Could not fetch article from URL")
    else:
        article_text = request.content

    if len(article_text.strip()) < 20:
        raise HTTPException(status_code=400, detail="Article text too short")

    await write_pending_analysis({
        "run_id": run_id,
        "article_text": article_text,
        "input_type": request.input_type,
        "created_at": datetime.utcnow().isoformat(),
        "status": "pending"
    })

    return {
        "run_id": run_id,
        "status": "queued",
        "message": "Article queued. Antigravity agents are processing."
    }

@app.get("/status/{run_id}")
async def check_status(run_id: str):
    """Flutter polls this until status is complete."""
    status = await get_pipeline_status()
    return status

@app.get("/report")
async def get_report():
    """Flutter reads final report after pipeline_status is complete."""
    report = await get_final_report()
    if not report:
        raise HTTPException(status_code=404, detail="No report available yet")
    return report

@app.post("/seed")
async def seed():
    """Seeds Firestore pricing_table with before-state data."""
    await seed_pricing_table()
    return {"status": "seeded", "message": "Pricing table restored to baseline"}
```

---

### `backend/requirements.txt` — REPLACE ENTIRELY

```
fastapi==0.111.0
uvicorn==0.29.0
firebase-admin==6.5.0
python-dotenv==1.0.0
httpx==0.27.0
beautifulsoup4==4.12.3
requests==2.32.0
pydantic==2.7.0
python-multipart==0.0.9
```

> **Remove:** `anthropic`, `google-generativeai` — NO LLM calls in backend anymore.

---

### `backend/services/firebase_client.py` — REPLACE ENTIRELY

```python
import firebase_admin
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter
import os
from dotenv import load_dotenv
import asyncio
from datetime import datetime

load_dotenv()

if not firebase_admin._apps:
    cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
    firebase_admin.initialize_app(cred)

db = firestore.client()

SEED_PRODUCTS = [
    {
        "id": "PROD-001",
        "name": "Standard Delivery — Lahore",
        "category": "logistics",
        "base_price_pkr": 180,
        "fuel_surcharge_pkr": 63,
        "total_price_pkr": 243,
        "margin_pct": 22.5,
        "last_updated": datetime.utcnow().isoformat(),
        "status": "active"
    },
    {
        "id": "PROD-002",
        "name": "Express Delivery — Karachi",
        "category": "logistics",
        "base_price_pkr": 250,
        "fuel_surcharge_pkr": 87,
        "total_price_pkr": 337,
        "margin_pct": 19.8,
        "last_updated": datetime.utcnow().isoformat(),
        "status": "active"
    },
    {
        "id": "PROD-003",
        "name": "Bulk Freight — Islamabad",
        "category": "freight",
        "base_price_pkr": 850,
        "fuel_surcharge_pkr": 297,
        "total_price_pkr": 1147,
        "margin_pct": 17.2,
        "last_updated": datetime.utcnow().isoformat(),
        "status": "active"
    },
    {
        "id": "PROD-004",
        "name": "Same-Day — Rawalpindi",
        "category": "express",
        "base_price_pkr": 320,
        "fuel_surcharge_pkr": 112,
        "total_price_pkr": 432,
        "margin_pct": 21.0,
        "last_updated": datetime.utcnow().isoformat(),
        "status": "active"
    },
    {
        "id": "PROD-005",
        "name": "Cold Chain — Multan",
        "category": "specialized",
        "base_price_pkr": 560,
        "fuel_surcharge_pkr": 196,
        "total_price_pkr": 756,
        "margin_pct": 14.5,
        "last_updated": datetime.utcnow().isoformat(),
        "status": "active"
    }
]

async def write_pending_analysis(data: dict):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None,
        lambda: db.collection("pending_analysis").document(data["run_id"]).set(data)
    )

async def get_pipeline_status():
    loop = asyncio.get_event_loop()
    doc = await loop.run_in_executor(
        None,
        lambda: db.collection("pipeline_status").document("current").get()
    )
    return doc.to_dict() if doc.exists else {"status": "processing"}

async def get_final_report():
    loop = asyncio.get_event_loop()
    doc = await loop.run_in_executor(
        None,
        lambda: db.collection("final_report").document("current").get()
    )
    return doc.to_dict() if doc.exists else None

async def seed_pricing_table():
    loop = asyncio.get_event_loop()
    def _seed():
        for product in SEED_PRODUCTS:
            db.collection("pricing_table").document(product["id"]).set(product)
        # also clear agent outputs for clean run
        for doc_id in ["agent1_result","agent2_result","agent3_result","agent4_result"]:
            db.collection("agent_outputs").document(doc_id).set({"status": "pending"})
        db.collection("pipeline_status").document("current").set({"status": "idle"})
    await loop.run_in_executor(None, _seed)
```

---

## 5. MCP Configuration — Create This New File

### `mcp.json` (in project root)

```json
{
  "mcp_servers": [
    {
      "name": "firebase-mcp",
      "type": "url",
      "url": "http://localhost:3001/sse",
      "description": "Firebase Firestore MCP server for Axion agent pipeline",
      "tools": [
        "firestore_read",
        "firestore_write",
        "firestore_batch_write",
        "firestore_listen",
        "firestore_delete"
      ]
    }
  ]
}
```

---

## 6. Firebase MCP Server — Create This New Folder

### `firebase/mcp_server/package.json`

```json
{
  "name": "axion-firebase-mcp",
  "version": "1.0.0",
  "description": "Firebase MCP server for Axion Antigravity agents",
  "main": "index.js",
  "scripts": {
    "start": "node index.js"
  },
  "dependencies": {
    "firebase-admin": "^12.0.0",
    "@modelcontextprotocol/sdk": "^1.0.0",
    "express": "^4.18.0",
    "dotenv": "^16.0.0"
  }
}
```

### `firebase/mcp_server/index.js`

```javascript
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
```

---

## 7. Updated `.env.example`

```
# Anthropic (used by Antigravity StrategyAgent + ComposerAgent)
ANTHROPIC_API_KEY=sk-ant-...

# Google Gemini (used by Antigravity AnalystAgent + ImpactAgent + ExecutorAgent)
GEMINI_API_KEY=AIza...

# Firebase
FIREBASE_PROJECT_ID=axion-demo
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# MCP Server
MCP_PORT=3001

# NewsAPI (optional, for URL scraping fallback)
NEWS_API_KEY=...

# App
PORT=8000
```

---

## 8. Dashboard — Rewire Data Source Only

The React dashboard components do NOT need to change. Only `src/services/api.js` changes.

### `dashboard/src/services/api.js` — REPLACE ENTIRELY

```javascript
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
```

---

## 9. Build & Run Order

Run these in order on hackathon day:

```bash
# Step 1: Start Firebase MCP server
cd firebase/mcp_server
npm install
node index.js
# Must be running on port 3001 before opening Antigravity

# Step 2: Seed Firestore with before-state
cd backend
pip install -r requirements.txt
python -c "import asyncio; from services.firebase_client import seed_pricing_table; asyncio.run(seed_pricing_table())"

# Step 3: Start backend
uvicorn main:app --reload --port 8000

# Step 4: Start dashboard
cd dashboard
npm install && npm run dev

# Step 5: Open Antigravity
# - Load the Axion project
# - Confirm mcp.json is detected (MCP panel should show firebase-mcp connected)
# - Open Manager View
# - Load .agents/ folder — all 5 agent .md files should appear
# - Configure trigger chain per pipeline_config.md

# Step 6: Trigger demo
# POST http://localhost:8000/demo
# Watch Antigravity Manager View — agents fire sequentially
# Dashboard auto-updates when pipeline_status becomes "complete"
```

---

## 10. Antigravity Manager View Setup

After opening Axion in Antigravity:

1. Open **Manager View** (multi-agent panel)
2. Create 3 workspaces:
   - **Workspace A** — load `01_analyst_agent.md` + `02_impact_agent.md`
   - **Workspace B** — load `03_strategy_agent.md`
   - **Workspace C** — load `04_executor_agent.md` + `05_composer_agent.md`
3. Set each workspace's model per `pipeline_config.md`
4. Connect MCP: Settings → MCP Servers → point to `mcp.json`
5. Run a test with demo input — confirm all 5 agents fire and `pipeline_status` becomes "complete"
6. Export the agent trace from Antigravity → save as `agent_trace.pdf` for submission

---

## 11. What This Proves to Judges

| Requirement | How Axion satisfies it |
|---|---|
| Antigravity is core orchestrator | All 5 agents run inside Antigravity Manager View |
| Multiple agents with structured reasoning | 5 sequential agents with Firestore trigger chain |
| Agent trace / logs from Antigravity | Exported automatically from Manager View |
| Action simulation | ExecutorAgent mutates Firestore pricing_table live |
| Before vs after state | simulation_state/before + after written by ExecutorAgent |
| Mobile app | Flutter polls pipeline_status, reads final_report |
| Proof of autonomy | Each agent reads previous agent's Firestore output — traceable chain |

---

## 12. Demo Script (3 minutes)

```
[0:00] Open Flutter app. Tap "Demo". Article submitted to Firestore.

[0:10] Switch to Antigravity Manager View on big screen.
       Show Workspace A firing — AnalystAgent extracting signals live.

[0:35] ImpactAgent fires — show it reading agent1_result from Firestore.
       "It's calculating PKR impact in real time."

[1:00] StrategyAgent fires — Claude Sonnet reasoning through 3 ranked actions.
       Show the reasoning steps in the Antigravity trace.

[1:25] ExecutorAgent fires — 3 simulations running.
       Switch to dashboard — pricing table updates LIVE.
       Before column: Rs. 243. After column: Rs. 278. Highlighted amber.

[1:50] ComposerAgent assembles final report. Flutter app updates automatically.
       Show execution log — 8 timestamped entries, all agents logged.

[2:10] Show Antigravity agent trace export.
       "Every decision is logged, traceable, and provable."

[2:30] "From news article to repriced business in under 20 seconds.
        Fully autonomous. Orchestrated by Antigravity."
```

---

*Axion v2.0 — Antigravity-Orchestrated Architecture*
*Stack: Google Antigravity · Claude Sonnet 4.6 · Claude Haiku 4.5 · Gemini 3 Flash · Gemini 3.1 Flash-Lite · Firebase Firestore MCP · Flutter · React*

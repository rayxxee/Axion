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

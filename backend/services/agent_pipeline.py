import os
import json
import time
from datetime import datetime
import google.generativeai as genai
from .firebase_client import db

from dotenv import load_dotenv
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

def get_gemini_response(prompt: str) -> dict:
    """Helper to call Gemini and parse JSON response."""
    # Using the standard model for all tasks to simplify deployment
    model = genai.GenerativeModel('gemini-flash-latest')
    response = model.generate_content(
        prompt + "\n\nCRITICAL INSTRUCTION: Your output MUST be ONLY valid JSON. Do not wrap in ```json fences. Return raw JSON string only."
    )
    text = response.text.strip()
    if text.startswith("```json"):
        text = text[7:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Failed to parse JSON: {text}")
        raise e

def log_execution(run_id, agent_name, action_desc, output_preview, index):
    """Helper to log execution steps."""
    log_data = {
        "agent": agent_name,
        "action": action_desc,
        "output_preview": output_preview,
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "run_id": run_id
    }
    db.collection("execution_log").document(f"log_{index}").set(log_data)


def run_pipeline(run_id: str, article_text: str):
    """Runs the 5-agent pipeline autonomously using Google Generative AI."""
    print(f"[{run_id}] Starting automated agent pipeline...")
    
    # Reset state
    db.collection("pipeline_status").document("current").set({"status": "processing"})
    
    try:
        # ---------------------------------------------------------
        # AGENT 1: Analyst Agent
        # ---------------------------------------------------------
        print(f"[{run_id}] Running AnalystAgent...")
        db.collection("pipeline_status").document("current").set({"status": "AnalystAgent: Extracting facts and parsing economic signals..."})
        prompt_1 = f"""
        You are a precision news extraction engine.
        Extract ONLY verifiable facts from the following article. No interpretation.
        
        Article: {article_text}
        
        Produce this exact JSON structure:
        {{
          "headline": "exact headline",
          "date": "YYYY-MM-DD or null",
          "topic": "monetary_policy|fuel_prices|taxation|trade|inflation|exchange_rate|other",
          "key_entities": ["list of entities"],
          "economic_signals": [
            {{
              "signal": "plain description",
              "magnitude": "exact number with unit",
              "direction": "up|down|neutral"
            }}
          ],
          "source_credibility_score": 0.8
        }}
        """
        agent1_result = get_gemini_response(prompt_1)
        db.collection("agent_outputs").document("agent1_result").set({
            "data": agent1_result,
            "status": "complete",
            "completed_at": datetime.utcnow().isoformat(),
            "run_id": run_id
        })
        log_execution(run_id, "AnalystAgent", "Extracted economic signals", agent1_result.get("headline", ""), 1)


        # ---------------------------------------------------------
        # AGENT 2: Impact Agent
        # ---------------------------------------------------------
        print(f"[{run_id}] Running ImpactAgent...")
        db.collection("pipeline_status").document("current").set({"status": "ImpactAgent: Calculating PKR business impact and margins..."})
        prompt_2 = f"""
        You are a Pakistan business impact analyst.
        Base Data:
        - Daily orders: 200, Avg order value: Rs. 3500, Base delivery cost: Rs. 180, Fuel component: 35%, Current margin: 18%.
        
        Economic Data Extracted:
        {json.dumps(agent1_result, indent=2)}
        
        Calculate REAL business consequences in PKR.
        Produce exact JSON structure:
        {{
          "impact_summary": "2 sentences max",
          "affected_sectors": ["logistics"],
          "quantified_metrics": {{
            "delivery_cost_change_pkr": <NUMBER>,
            "delivery_cost_change_pct": <NUMBER>,
            "margin_change_pct": <NUMBER negative means compression>,
            "affected_orders_per_day": 200,
            "monthly_revenue_impact_pkr": <NUMBER>,
            "breakeven_price_increase_pct": <NUMBER>
          }},
          "severity": "low|medium|high|critical",
          "severity_rationale": "one sentence"
        }}
        """
        agent2_result = get_gemini_response(prompt_2)
        db.collection("agent_outputs").document("agent2_result").set({
            "data": agent2_result, "status": "complete"
        })
        log_execution(run_id, "ImpactAgent", "Calculated PKR business impact", agent2_result.get("severity", ""), 2)


        # ---------------------------------------------------------
        # AGENT 3: Strategy Agent
        # ---------------------------------------------------------
        print(f"[{run_id}] Running StrategyAgent...")
        db.collection("pipeline_status").document("current").set({"status": "StrategyAgent: Generating defensive business actions..."})
        prompt_3 = f"""
        You are a senior Pakistan business strategy advisor.
        Impact Data:
        {json.dumps(agent2_result, indent=2)}
        
        Generate exactly 3 ranked, executable business actions (simulate=true for Rank 1 only).
        JSON structure:
        {{
          "actions": [
            {{
              "rank": 1,
              "title": "...",
              "rationale": "...",
              "steps": ["..."],
              "expected_outcome": "...",
              "effort": "low",
              "impact": "high",
              "timeframe": "immediate",
              "simulate": true
            }}
          ],
          "decision_rationale": "..."
        }}
        """
        agent3_result = get_gemini_response(prompt_3)
        db.collection("agent_outputs").document("agent3_result").set({
            "data": agent3_result, "status": "complete"
        })
        log_execution(run_id, "StrategyAgent", "Generated 3 ranked actions", "Rank 1 generated", 3)


        # ---------------------------------------------------------
        # AGENT 4: Executor Agent
        # ---------------------------------------------------------
        print(f"[{run_id}] Running ExecutorAgent...")
        db.collection("pipeline_status").document("current").set({"status": "ExecutorAgent: Simulating price adjustments and notifications..."})
        # Fetch pricing table natively
        pricing_docs = db.collection("pricing_table").stream()
        before_state = [doc.to_dict() for doc in pricing_docs]
        db.collection("simulation_state").document("before").set({"state": before_state})

        prompt_4 = f"""
        You are the execution agent simulating the Rank 1 action.
        Impact Data: {json.dumps(agent2_result, indent=2)}
        Actions: {json.dumps(agent3_result, indent=2)}
        Before State Pricing: {json.dumps(before_state, indent=2)}
        
        1. Recalculate prices applying breakeven_price_increase_pct. Round to nearest 5.
        2. Draft Notifications.
        3. Draft Workflow alert.
        
        Produce exact JSON structure (IMPORTANT: price_pkr MUST BE A RAW NUMBER, e.g. 250, NOT "Rs. 250"):
        {{
          "after_state": [
            {{ "id": "...", "name": "...", "price_pkr": <NUMBER> }}
          ],
          "notification_draft": {{
            "email": {{"subject":"...", "body":"..."}},
            "sms": {{"body":"..."}},
            "internal_alert": "..."
          }},
          "workflow_alert": {{
            "priority":"P1", "category":"pricing", "title":"...", "description":"...", "required_actions":[]
          }}
        }}
        """
        agent4_result = get_gemini_response(prompt_4)
        after_state = agent4_result.get("after_state", [])
        for product in after_state:
            prod_id = product.get("id")
            if prod_id:
                db.collection("pricing_table").document(prod_id).set({"total_price_pkr": product.get("price_pkr")}, merge=True)
                
        db.collection("simulation_state").document("after").set({"state": after_state})
        db.collection("notification_drafts").document("current").set(agent4_result.get("notification_draft", {}))
        db.collection("workflow_alerts").document("current").set(agent4_result.get("workflow_alert", {}))
        db.collection("agent_outputs").document("agent4_result").set({
            "data": agent4_result,
            "status": "complete"
        })
        log_execution(run_id, "ExecutorAgent:PricingUpdater", "Updated pricing_table in Firestore", "New prices calculated", 4)
        log_execution(run_id, "ExecutorAgent:NotifDrafter", "Generated email and SMS drafts", "Notifications drafted", 5)
        log_execution(run_id, "ExecutorAgent:WorkflowTrigger", "Created P1 stakeholder alert", "Workflow alert created", 6)


        # ---------------------------------------------------------
        # AGENT 5: Composer Agent
        # ---------------------------------------------------------
        print(f"[{run_id}] Running ComposerAgent...")
        db.collection("pipeline_status").document("current").set({"status": "ComposerAgent: Assembling final interactive report..."})
        prompt_5 = f"""
        You are the output composer. Organize everything into the final report.
        Format PKR amounts as "Rs. X,XXX" where applicable EXCEPT for impact_metrics, before_state, and after_state price fields which must be raw numbers.
        
        Data Context:
        Analyst: {json.dumps(agent1_result, indent=2)}
        Impact: {json.dumps(agent2_result, indent=2)}
        Strategy: {json.dumps(agent3_result, indent=2)}
        Executor: {json.dumps(agent4_result, indent=2)}
        
        Produce EXACT JSON structure (IMPORTANT: cost_change_pkr, margin_change_pct, and all price fields MUST BE NUMBERS):
        {{
          "run_id": "{run_id}",
          "insight_card": {{
            "headline": "...",
            "topic_badge": "...",
            "severity": "...",
            "credibility_score": 0.95,
            "one_line_insight": "..."
          }},
          "impact_metrics": {{
            "cost_change_pkr": <NUMBER>,
            "margin_change_pct": <NUMBER negative for compression>,
            "affected_orders_count": 200,
            "risk_level": "..."
          }},
          "actions": <ARRAY_FROM_STRATEGY>,
          "before_state": {json.dumps(before_state)},
          "after_state": <ARRAY_FROM_EXECUTOR_AFTER_STATE>,
          "notification_draft": <OBJECT_FROM_EXECUTOR>,
          "state_change_summary": "..."
        }}
        """
        final_report = get_gemini_response(prompt_5)
        
        # Grab logs
        logs = [doc.to_dict() for doc in db.collection("execution_log").stream()]
        final_report["execution_log"] = sorted(logs, key=lambda x: x.get("timestamp", ""))
        
        db.collection("final_report").document("current").set(final_report)
        log_execution(run_id, "ComposerAgent", "Assembled final report", "Pipeline Complete", 5)

        # Finish
        db.collection("pipeline_status").document("current").set({"status": "complete"})
        print(f"[{run_id}] Pipeline execution completed successfully.")
        
    except Exception as e:
        print(f"[{run_id}] Pipeline error: {e}")
        db.collection("pipeline_status").document("current").set({"status": "error", "error_message": str(e)})

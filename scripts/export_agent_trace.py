"""Export Antigravity agent execution logs from Firestore for hackathon submission."""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def export_trace():
    """Read execution_log collection from Firestore and export formatted JSON."""
    if not firebase_admin._apps:
        cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")
        if not os.path.isabs(cred_path):
            cred_path = os.path.join(os.path.dirname(__file__), "..", cred_path)
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # Fetch execution log
    logs = db.collection("execution_log").order_by("timestamp").stream()
    log_entries = [doc.to_dict() for doc in logs]

    # Fetch pipeline status
    status_doc = db.collection("pipeline_status").document("current").get()
    pipeline_status = status_doc.to_dict() if status_doc.exists else {}

    # Extract Workplan & Tasks Plan from standard pipeline definitions
    workplan = {
        "architecture": "Google Antigravity Manager View",
        "workspaces": [
            {"id": "Workspace A", "agents": ["AnalystAgent", "ImpactAgent"], "trigger": "Firestore pending_analysis"},
            {"id": "Workspace B", "agents": ["StrategyAgent"], "trigger": "ImpactAgent completion"},
            {"id": "Workspace C", "agents": ["ExecutorAgent", "ComposerAgent"], "trigger": "StrategyAgent completion"}
        ]
    }

    # Extract Reasoning Steps and Decision Flow
    reasoning_steps = []
    decision_flow = []
    action_execution = []

    for idx, entry in enumerate(log_entries):
        agent = entry.get("agent", "Unknown")
        action = entry.get("action", "")
        status = entry.get("status", "")
        
        step_summary = f"[{agent}] {action} -> {status}"
        decision_flow.append(f"Step {idx + 1}: {step_summary}")
        
        reasoning_steps.append({
            "agent": agent,
            "logic_applied": action,
            "output": entry.get("output_preview", "")
        })

        if "ExecutorAgent" in agent or "ComposerAgent" in agent:
            action_execution.append({
                "agent": agent,
                "execution_type": action,
                "result_preview": entry.get("output_preview", ""),
                "timestamp": entry.get("timestamp", "")
            })

    trace = {
        "export_metadata": {
            "timestamp": datetime.utcnow().isoformat(),
            "pipeline_status": pipeline_status,
            "total_agents_executed": len(log_entries),
        },
        "deliverable_sections": {
            "1_workplan_and_tasks_plan": workplan,
            "2_decision_flow": decision_flow,
            "3_reasoning_steps": reasoning_steps,
            "4_action_execution": action_execution,
            "5_raw_execution_log": log_entries
        }
    }

    output_path = os.path.join(os.path.dirname(__file__), "..", "agent_trace.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)

    print(f"Exported deliverable trace to {os.path.abspath(output_path)}")


if __name__ == "__main__":
    export_trace()

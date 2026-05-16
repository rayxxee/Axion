"""Export Antigravity agent execution logs from Firestore for hackathon submission."""

import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


def export_trace():
    """Read execution_log collection from Firestore and export as JSON."""
    if not firebase_admin._apps:
        cred = credentials.Certificate(os.getenv("FIREBASE_CREDENTIALS_PATH"))
        firebase_admin.initialize_app(cred)

    db = firestore.client()

    # Fetch execution log
    logs = db.collection("execution_log").order_by("timestamp").stream()
    log_entries = [doc.to_dict() for doc in logs]

    # Fetch pipeline status
    status_doc = db.collection("pipeline_status").document("current").get()
    pipeline_status = status_doc.to_dict() if status_doc.exists else {}

    trace = {
        "export_timestamp": datetime.utcnow().isoformat(),
        "pipeline_status": pipeline_status,
        "total_agents": len(log_entries),
        "execution_log": log_entries
    }

    output_path = os.path.join(os.path.dirname(__file__), "..", "agent_trace.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(trace, f, indent=2, ensure_ascii=False)

    print(f"Exported {len(log_entries)} log entries to {os.path.abspath(output_path)}")


if __name__ == "__main__":
    export_trace()

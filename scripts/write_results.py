import sys
import json
import os
sys.path.append(os.path.abspath('.'))
from backend.services.firebase_client import db

data = {
    "data": {
        "headline": "The Pakistani Rupee depreciated by 3% against the US Dollar in interbank trading today",
        "date": None,
        "topic": "exchange_rate",
        "key_entities": ["Pakistani Rupee", "US Dollar"],
        "economic_signals": [
            {
                "signal": "Pakistani Rupee depreciated against the US Dollar in interbank trading",
                "magnitude": "3%",
                "direction": "down"
            },
            {
                "signal": "Interbank closing exchange rate",
                "magnitude": "Rs 289.50",
                "direction": "down"
            }
        ],
        "source_credibility_score": 0.8
    },
    "completed_at": "2026-05-20T17:52:22+05:00",
    "status": "complete",
    "run_id": "7b942d05-0f2e-474a-935a-4902c98885a8"
}

db.collection("agent_outputs").document("agent1_result").set(data, merge=True)

log_data = {
    "agent": "AnalystAgent",
    "action": "Extracted economic signals from article",
    "output_preview": "Pakistani Rupee depreciated by 3%...",
    "status": "success",
    "timestamp": "2026-05-20T17:52:22+05:00",
    "run_id": "7b942d05-0f2e-474a-935a-4902c98885a8"
}

db.collection("execution_log").document("log_1").set(log_data, merge=True)

print("Writes completed.")

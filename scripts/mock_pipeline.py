import os
import sys
import time
import json
from datetime import datetime

sys.path.append(os.path.abspath('..'))
from backend.services.firebase_client import db

def run():
    print("Fetching pending analysis...")
    docs = db.collection('pending_analysis').order_by('created_at', direction='DESCENDING').limit(1).stream()
    doc = next(docs, None)
    if not doc:
        print("No pending analysis found.")
        return
    data = doc.to_dict()
    run_id = data.get('run_id', 'unknown')
    
    print(f"Running pipeline for {run_id}...")
    db.collection('pipeline_status').document('current').set({"status": "processing"})
    
    # Agent 1
    time.sleep(2)
    db.collection('agent_outputs').document('agent1_result').set({
        "status": "complete",
        "data": {
            "headline": "SBP raises policy rate by 200 bps",
            "topic": "monetary_policy",
            "economic_signals": [{"signal": "Policy rate increased", "magnitude": "200bps", "direction": "up"}],
            "source_credibility_score": 0.9
        },
        "completed_at": datetime.utcnow().isoformat()
    })
    print("Agent 1 complete.")
    
    # Agent 2
    time.sleep(2)
    db.collection('agent_outputs').document('agent2_result').set({
        "status": "complete",
        "data": {
            "delivery_cost_increase": "15%",
            "severity_rating": "High"
        },
        "completed_at": datetime.utcnow().isoformat()
    })
    print("Agent 2 complete.")
    
    # Agent 3
    time.sleep(2)
    db.collection('agent_outputs').document('agent3_result').set({
        "status": "complete",
        "data": {
            "actions": [
                {"rank": 1, "title": "Adjust Pricing", "effort": "Low", "impact": "High"}
            ]
        },
        "completed_at": datetime.utcnow().isoformat()
    })
    print("Agent 3 complete.")
    
    # Agent 4
    time.sleep(2)
    db.collection('agent_outputs').document('agent4_result').set({
        "status": "complete",
        "data": {
            "simulations_run": 3
        },
        "completed_at": datetime.utcnow().isoformat()
    })
    print("Agent 4 complete.")
    
    # Final Report
    time.sleep(2)
    db.collection('final_report').document('current').set({
        "run_id": run_id,
        "summary": "SBP rate hike increases borrowing costs. Recommended to adjust logistics pricing by 15% to maintain margins.",
        "before_after": [
            {"product": "Standard Delivery - Lahore", "before": 243, "after": 280, "margin": "18%"}
        ],
        "notifications": {
            "email": "Dear customer, due to the recent SBP rate hike...",
            "sms": "Muaziz sarif, delivery charges have been updated..."
        },
        "alerts": [
            {"level": "P1", "message": "Update pricing table in production"}
        ]
    })
    
    # Pipeline complete
    db.collection('pipeline_status').document('current').set({"status": "complete"})
    print("Pipeline complete!")

if __name__ == '__main__':
    run()

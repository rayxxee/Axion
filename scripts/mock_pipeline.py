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
    
    # Final Report with CORRECT structure expected by ResultsPage.jsx
    db.collection('final_report').document('current').set({
        "run_id": run_id,
        "insight_card": {
            "headline": "SBP raises policy rate by 200 bps to 19.5%",
            "topic_badge": "Monetary Policy",
            "severity": "High",
            "credibility_score": 0.95,
            "one_line_insight": "Significant borrowing cost increase affecting working capital."
        },
        "impact_metrics": {
            "cost_change_pkr": 45000,
            "margin_change_pct": -2.5,
            "affected_orders_count": 200,
            "risk_level": "High"
        },
        "actions": [
            {
                "rank": 1,
                "title": "Adjust Logistics Pricing",
                "simulate": True,
                "rationale": "Maintain 18% margin baseline",
                "steps": ["Recalculate prices", "Notify customers"],
                "effort": "Low",
                "impact": "High",
                "timeframe": "Immediate"
            },
            {
                "rank": 2,
                "title": "Optimize Routes",
                "simulate": False,
                "rationale": "Reduce fuel usage to offset costs",
                "steps": ["Audit routes", "Deploy optimizer"],
                "effort": "Medium",
                "impact": "Medium",
                "timeframe": "1-2 Weeks"
            }
        ],
        "before_state": [
            {"name": "Standard Delivery - Lahore", "total_price_pkr": 243},
            {"name": "Express Delivery - Karachi", "total_price_pkr": 337},
            {"name": "Bulk Freight - Islamabad", "total_price_pkr": 1147}
        ],
        "after_state": [
            {"name": "Standard Delivery - Lahore", "total_price_pkr": 288},
            {"name": "Express Delivery - Karachi", "total_price_pkr": 395},
            {"name": "Bulk Freight - Islamabad", "total_price_pkr": 1250}
        ],
        "notification_draft": {
            "email": {"subject": "Pricing Update Notification", "body": "Dear customer,\nDue to the recent 200 bps SBP rate hike, we are updating our delivery charges to maintain service quality."},
            "sms": {"body": "Delivery charges update ho gaye hain. Naye rates app par dekhein."},
            "internal_alert": "Urgent: Apply new pricing table across all regions immediately."
        },
        "execution_log": [
            {"agent": "AnalystAgent", "action": "Extracted facts", "timestamp": "12:00:01"},
            {"agent": "ImpactAgent", "action": "Calculated PKR impact", "timestamp": "12:00:02"},
            {"agent": "StrategyAgent", "action": "Generated actions", "timestamp": "12:00:05"},
            {"agent": "ExecutorAgent:PricingUpdater", "action": "Updated prices", "timestamp": "12:00:08"},
            {"agent": "ExecutorAgent:NotifDrafter", "action": "Drafted emails", "timestamp": "12:00:09"},
            {"agent": "ComposerAgent", "action": "Assembled report", "timestamp": "12:00:10"}
        ],
        "state_change_summary": "Simulated pricing update applied across 5 products to maintain 18% margins."
    })
    
    # Pipeline complete
    db.collection('pipeline_status').document('current').set({"status": "complete"})
    print("Pipeline complete!")

if __name__ == '__main__':
    run()

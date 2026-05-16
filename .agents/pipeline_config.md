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

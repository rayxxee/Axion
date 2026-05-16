# Axion — News-to-Policy Impact Analyzer

A 5-agent AI pipeline that ingests news articles, analyzes business impact for the Pakistani market, generates ranked actions, and simulates execution — all visible in a before/after dashboard.

## Architecture

- **Backend**: FastAPI (Python 3.11) + 5 sequential LLM agents (Anthropic Claude)
- **Database**: Firebase Firestore (pricing table simulation)
- **Web Dashboard**: React + Tailwind CSS
- **Mobile**: Flutter (Android)
- **LLM**: Claude Opus 4 (planning) + Claude Sonnet 4 (execution)

## Quick Start

```bash
# 1. Backend
cd backend && pip install -r requirements.txt
cp ../.env.example ../.env  # fill in API keys
uvicorn main:app --reload --port 8000

# 2. Dashboard
cd dashboard && npm install && npm run dev

# 3. Mobile
cd mobile && flutter run
```

## Demo Inputs

- "SBP raises interest rate by 200bps"
- "Petrol price increased by 18%"
- "PKR depreciates 3% against USD"

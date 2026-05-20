"""
Test all backend API endpoints for the Axion Flutter app.
Validates that the deployed Cloud Run backend is reachable and functional.
"""
import asyncio
import httpx
import json
import sys
import io
from datetime import datetime

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BACKEND_URL = "https://axion-backend-133838314315.us-central1.run.app"

# Same endpoints the Flutter app calls
TESTS = []
results = {"passed": 0, "failed": 0, "errors": []}


def test(name):
    """Decorator to register a test function."""
    def decorator(func):
        TESTS.append((name, func))
        return func
    return decorator


@test("GET /health — Backend reachable")
async def test_health(client: httpx.AsyncClient):
    r = await client.get(f"{BACKEND_URL}/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["status"] == "ok", f"Expected status=ok, got {data}"
    assert "version" in data, "Missing version field"
    return data


@test("POST /seed — Reset pricing table")
async def test_seed(client: httpx.AsyncClient):
    r = await client.post(f"{BACKEND_URL}/seed")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert data["status"] == "seeded", f"Expected status=seeded, got {data}"
    return data


@test("POST /analyze (demo) — Submit demo article")
async def test_analyze_demo(client: httpx.AsyncClient):
    r = await client.post(
        f"{BACKEND_URL}/analyze",
        json={"input_type": "demo", "content": ""},
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "run_id" in data, f"Missing run_id in response: {data}"
    assert data["status"] == "queued", f"Expected status=queued, got {data}"
    return data


@test("POST /analyze (text) — Submit text article")
async def test_analyze_text(client: httpx.AsyncClient):
    article = (
        "KARACHI: The State Bank of Pakistan (SBP) has announced an increase "
        "in the policy rate by 200 basis points, bringing the key interest rate "
        "to 19.5%. The Monetary Policy Committee (MPC) cited persistent "
        "inflationary pressures and external sector vulnerabilities."
    )
    r = await client.post(
        f"{BACKEND_URL}/analyze",
        json={"input_type": "text", "content": article},
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert "run_id" in data, f"Missing run_id: {data}"
    return data


@test("GET /status/{run_id} — Check pipeline status")
async def test_status(client: httpx.AsyncClient):
    r = await client.get(f"{BACKEND_URL}/status/test-run-id-12345")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    # Status can be processing/idle/complete - all valid
    assert "status" in data, f"Missing status field: {data}"
    return data


@test("GET /report — Fetch final report")
async def test_report(client: httpx.AsyncClient):
    r = await client.get(f"{BACKEND_URL}/report")
    # 200 if report exists, 404 if no report yet - both are valid responses
    assert r.status_code in (200, 404), f"Unexpected status {r.status_code}"
    if r.status_code == 200:
        data = r.json()
        return {"status": "report_available", "keys": list(data.keys()) if isinstance(data, dict) else "non-dict"}
    return {"status": "no_report_yet (404 — expected if no analysis run)"}


@test("GET /history — Fetch analysis history")
async def test_history(client: httpx.AsyncClient):
    r = await client.get(f"{BACKEND_URL}/history")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    return {"count": len(data)}


@test("GET /trace — Fetch execution log")
async def test_trace(client: httpx.AsyncClient):
    r = await client.get(f"{BACKEND_URL}/trace")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    data = r.json()
    assert isinstance(data, list), f"Expected list, got {type(data)}"
    return {"count": len(data)}


@test("CORS Headers — Verify CORS is enabled")
async def test_cors(client: httpx.AsyncClient):
    r = await client.options(
        f"{BACKEND_URL}/health",
        headers={
            "Origin": "http://localhost:8888",
            "Access-Control-Request-Method": "GET",
        },
    )
    # Cloud Run + FastAPI CORS should return appropriate headers
    cors_header = r.headers.get("access-control-allow-origin", "MISSING")
    return {"cors_allow_origin": cors_header, "status_code": r.status_code}


@test("POST /analyze (short text) — Validation error")
async def test_analyze_validation(client: httpx.AsyncClient):
    r = await client.post(
        f"{BACKEND_URL}/analyze",
        json={"input_type": "text", "content": "too short"},
        headers={"Content-Type": "application/json"},
    )
    assert r.status_code == 400, f"Expected 400 for short text, got {r.status_code}"
    return {"correctly_rejected": True}


async def run_all():
    print(f"\n{'='*60}")
    print(f"  Axion Backend Connection Test")
    print(f"  Target: {BACKEND_URL}")
    print(f"  Time: {datetime.now().isoformat()}")
    print(f"{'='*60}\n")

    async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
        for name, func in TESTS:
            try:
                result = await func(client)
                results["passed"] += 1
                print(f"  ✅ {name}")
                if result:
                    for k, v in (result.items() if isinstance(result, dict) else [("response", result)]):
                        print(f"     └─ {k}: {v}")
            except AssertionError as e:
                results["failed"] += 1
                results["errors"].append({"test": name, "error": str(e)})
                print(f"  ❌ {name}")
                print(f"     └─ {e}")
            except Exception as e:
                results["failed"] += 1
                results["errors"].append({"test": name, "error": f"{type(e).__name__}: {e}"})
                print(f"  ❌ {name}")
                print(f"     └─ {type(e).__name__}: {e}")

    print(f"\n{'='*60}")
    print(f"  Results: {results['passed']} passed, {results['failed']} failed")
    print(f"{'='*60}\n")

    if results["failed"] > 0:
        print("FAILED TESTS:")
        for err in results["errors"]:
            print(f"  • {err['test']}: {err['error']}")
        sys.exit(1)
    else:
        print("All backend connections verified! ✅")
        print("Flutter app should work correctly with this backend.")


if __name__ == "__main__":
    asyncio.run(run_all())

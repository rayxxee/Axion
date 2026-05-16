"""Route integration tests."""


def test_health(client):
    """Health endpoint returns ok."""
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_analyze_returns_202(client):
    """POST /analyze returns 202 with job_id."""
    resp = client.post("/api/v1/analyze", json={
        "input_type": "text",
        "content": "SBP raises interest rate by 200 basis points effective June 2026",
    })
    assert resp.status_code == 202
    data = resp.json()
    assert "job_id" in data
    assert "stream_url" in data


def test_analyze_rejects_short_content(client):
    """POST /analyze rejects content under 10 chars."""
    resp = client.post("/api/v1/analyze", json={
        "input_type": "text",
        "content": "short",
    })
    assert resp.status_code == 422


def test_list_jobs(client):
    """GET /jobs returns a list."""
    resp = client.get("/api/v1/jobs")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

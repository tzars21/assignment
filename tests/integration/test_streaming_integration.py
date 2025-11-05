import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_streaming_chunks():
    session_id = "integration-session"
    data = {"session_id": session_id, "query": "Hello world"}
    resp = client.post("/chat/stream", json=data, stream=True)
    assert resp.status_code == 200
    lines = []
    for line in resp.iter_lines():
        if line:
            lines.append(line.decode())
    assert len(lines) >= 2
    assert any('done' in l or 'token' in l for l in lines)

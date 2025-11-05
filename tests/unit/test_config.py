import os
from app.config import Settings, settings
import pytest

def test_settings_loads_env(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "abc123")
    monkeypatch.setenv("AGNO_API_PROVIDER", "openai")
    monkeypatch.setenv("MAX_UPLOAD_BYTES", "1024")
    s = Settings()
    assert s.openai_api_key == "abc123"
    assert s.provider == "openai"
    assert s.max_upload_bytes == 1024

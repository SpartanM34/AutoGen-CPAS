import pytest

pytest.importorskip("flask")
import json

from api.tbeep_api import MESSAGE_STORE, app


def test_post_and_get_message():
    client = app.test_client()
    MESSAGE_STORE.clear()
    msg = {
        "thread_id": "#TEST_001.0",
        "instance": "Unit",
        "reasoningLevel": "Detailed",
        "confidence": "High",
        "collaborationMode": "Discussion",
        "timestamp": "2025-01-01T00:00:00Z",
        "version": "#TEST.v1.0",
        "content": "hello"
    }
    res = client.post("/api/v1/messages", json=msg)
    assert res.status_code == 201
    res = client.get("/api/v1/messages", query_string={"thread_id": "#TEST_001.0"})
    assert res.status_code == 200
    assert res.get_json() == [msg]


def test_missing_thread_id():
    client = app.test_client()
    MESSAGE_STORE.clear()
    res = client.post("/api/v1/messages", json={"content": "x"})
    assert res.status_code == 400


def test_invalid_json():
    client = app.test_client()
    MESSAGE_STORE.clear()
    # send malformed JSON payload
    res = client.post(
        "/api/v1/messages",
        data="{bad json",
        content_type="application/json",
    )
    assert res.status_code == 400


def test_get_missing_thread_returns_empty():
    client = app.test_client()
    MESSAGE_STORE.clear()
    res = client.get("/api/v1/messages", query_string={"thread_id": "missing"})
    assert res.status_code == 200
    assert res.get_json() == []


def test_post_multiple_messages():
    client = app.test_client()
    MESSAGE_STORE.clear()
    thread_id = "#TEST_MULTI"
    msg1 = {"thread_id": thread_id, "content": "one"}
    msg2 = {"thread_id": thread_id, "content": "two"}
    res = client.post("/api/v1/messages", json=msg1)
    assert res.status_code == 201
    res = client.post("/api/v1/messages", json=msg2)
    assert res.status_code == 201
    res = client.get("/api/v1/messages", query_string={"thread_id": thread_id})
    assert res.status_code == 200
    assert res.get_json() == [msg1, msg2]

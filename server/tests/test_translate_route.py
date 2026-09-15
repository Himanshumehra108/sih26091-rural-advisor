from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_translate_route_returns_translation_payload():
    response = client.post(
        "/api/translate",
        json={"text": "Welcome to Rural Advisor", "target_language": "hi-IN"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "translated_text" in payload
    assert payload["target_language"] == "hi-IN"
    assert payload["source_language"] == "en-IN"

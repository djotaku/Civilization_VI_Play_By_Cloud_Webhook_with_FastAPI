from fastapi.testclient import TestClient

from civ_vi_webhook.main import app

client = TestClient(app)


def test_webhook_good_data():
    response = client.post("/webhook", json={"value1": "Eric's Barbarian Game", "value2": "Eric", "value3": "300"})
    assert response.status_code == 201

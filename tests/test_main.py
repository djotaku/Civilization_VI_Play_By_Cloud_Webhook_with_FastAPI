from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from civ_vi_webhook.main import app
import civ_vi_webhook.main


client = TestClient(app)


@patch.object(civ_vi_webhook.main, 'current_games', {})
def test_webhook_good_data():
    response = client.post("/webhook", json={"value1": "Eric's Barbarian Game", "value2": "Eric", "value3": "300"})
    assert response.status_code == 201

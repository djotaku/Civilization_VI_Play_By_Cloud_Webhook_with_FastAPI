from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from civ_vi_webhook.main import app
import civ_vi_webhook.main


client = TestClient(app)
matrix_bot_mock = Mock()


@patch.object(civ_vi_webhook.main, 'current_games', {})
@patch.object(civ_vi_webhook.main.api_matrix_bot, 'main', matrix_bot_mock)
def test_webhook_good_data():
    response = client.post("/webhook", json={"value1": "Eric's Barbarian Clash Game", "value2": "Eric", "value3": "300"})
    assert response.status_code == 201
    assert civ_vi_webhook.main.current_games["Eric's Barbarian Clash Game"]["player_name"] == "Eric"
    assert civ_vi_webhook.main.current_games["Eric's Barbarian Clash Game"]["turn_number"] == "300"


@patch.object(civ_vi_webhook.main, 'current_games', {})
@patch.object(civ_vi_webhook.main.api_matrix_bot, 'main', matrix_bot_mock)
def test_webhook_duplicate_data():
    client.post("/webhook", json={"value1": "Eric's Barbarian Clash Game", "value2": "Eric", "value3": "300"})
    response = client.post("/webhook", json={"value1": "Eric's Barbarian Clash Game", "value2": "Eric", "value3": "300"})
    assert response.status_code == 429


@patch.object(civ_vi_webhook.main, 'current_games', {})
def test_webhook_message():
    with patch.object(civ_vi_webhook.main.api_matrix_bot, 'main') as mock:
        client.post("/webhook", json={"value1": "Eric's Barbarian Clash Game", "value2": "Eric", "value3": "300"})
    mock.assert_called_with("Hey, Eric, it's your turn in Eric's Barbarian Clash Game. The game is on turn 300")


@patch.object(civ_vi_webhook.main, 'current_games', {})
@patch.object(civ_vi_webhook.main.api_matrix_bot, 'main', matrix_bot_mock)
def test_pydt_good_data():
    response = client.post("/pydt", json={"value1": "Eric's Barbarian Clash Game", "value2": "Eric", "value3": "300",
                                          "gameName": "Eric's Barbarian Clash Game",
                                          "userName": "Eric",
                                          "round": 300,
                                          "civName": "Sumeria",
                                          "leaderName": "Gilgamesh"
                                          })
    assert response.status_code == 201
    assert civ_vi_webhook.main.current_games["Eric's Barbarian Clash Game"]["player_name"] == "Eric"
    assert civ_vi_webhook.main.current_games["Eric's Barbarian Clash Game"]["turn_number"] == 300


@patch.object(civ_vi_webhook.main, 'current_games', {})
def test_pydt_message():
    with patch.object(civ_vi_webhook.main.api_matrix_bot, 'main') as mock:
        response = client.post("/pydt", json={"value1": "Eric's Barbarian Clash Game", "value2": "Eric", "value3": "300",
                                              "gameName": "Eric's Barbarian Clash Game",
                                              "userName": "Eric",
                                              "round": 300,
                                              "civName": "Sumeria",
                                              "leaderName": "Gilgamesh"
                                              })
    mock.assert_called_with("Hey, Eric, Gilgamesh is waiting for you to command Sumeria in Eric's Barbarian Clash Game. The game is on turn 300")


current_games_for_endpoint = {"Eric's Barbarian Clash Game": {"player_name": "Eric", "turn_number": 300,
                                                              "time_stamp": {"year": 2021, "month": 10,
                                                                             "day": 3, "hour": 13, "minute": 15,
                                                                             "second": 4}}}


@patch.object(civ_vi_webhook.main, 'current_games', current_games_for_endpoint)
def test_return_current_games():
    response = client.get("/current_games")
    assert response.status_code == 200
    assert response.json() == {"Eric's Barbarian Clash Game": {"player_name": "Eric", "turn_number": 300,
                                                               "time_stamp": {"year": 2021, "month": 10,
                                                                              "day": 3, "hour": 13, "minute": 15,
                                                                              "second": 4}}}


@patch.object(civ_vi_webhook.main, 'current_games', current_games_for_endpoint)
def test_return_current_games_ask_for_eric():
    response = client.get("/current_games?player_to_blame=Eric")
    assert response.status_code == 200
    assert response.json() == {"Eric's Barbarian Clash Game": {"player_name": "Eric", "turn_number": 300,
                                                               "time_stamp": {"year": 2021, "month": 10,
                                                                              "day": 3, "hour": 13, "minute": 15,
                                                                              "second": 4}}}


@patch.object(civ_vi_webhook.main, 'current_games', current_games_for_endpoint)
def test_return_current_games_ask_for_stella():
    response = client.get("/current_games?player_to_blame=Stella")
    assert response.status_code == 404
    assert response.json() == {"detail": "Player not found"}


@patch.object(civ_vi_webhook.main, 'current_games', {})
def test_return_total_number_of_games():
    response = client.get("/total_number_of_games")
    assert response.status_code == 200
    assert response.text == "0"
    civ_vi_webhook.main.current_games = {"Eric's Barbarian Clash Game": {"player_name": "Eric", "turn_number": 300,
                                                                         "time_stamp": {"year": 2021, "month": 10,
                                                                                        "day": 3, "hour": 13,
                                                                                        "minute": 15, "second": 4}}}
    response = client.get("/total_number_of_games")
    assert response.status_code == 200
    assert response.text == "1"
    civ_vi_webhook.main.current_games["Eric's Barbarian Clash Game 2"] = {"player_name": "Eric", "turn_number": 300,
                                                                          "time_stamp": {"year": 2021, "month": 10,
                                                                                         "day": 3, "hour": 13,
                                                                                         "minute": 15, "second": 4}}
    response = client.get("/total_number_of_games")
    assert response.status_code == 200
    assert response.text == "2"


@patch.object(civ_vi_webhook.main, 'current_games', {})
def test_delete_game():
    # first try to delete a game that isn't there
    response = client.delete('/delete_game?game_to_delete=A Game')
    assert response.status_code == 404
    civ_vi_webhook.main.current_games = {"Eric's Barbarian Clash Game": {"player_name": "Eric", "turn_number": 300,
                                                                         "time_stamp": {"year": 2021, "month": 10,
                                                                                        "day": 3, "hour": 13,
                                                                                        "minute": 15, "second": 4}}}
    response = client.delete("/delete_game?game_to_delete=Eric's Barbarian Clash Game")
    assert response.status_code == 200
    assert civ_vi_webhook.main.current_games == {}
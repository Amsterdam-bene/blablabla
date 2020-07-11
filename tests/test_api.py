import json

from api import QUERY_ENDPOINT, HEALTH_ENDPOINT
from bot.adapter import MarkovifyAdapter


def check_response(client, body, headers=None, expected_text=None):
    if headers is None:
        headers = {"content-type": "application/json"}
    response = client.simulate_post(QUERY_ENDPOINT, json=body, headers=headers)

    assert response
    assert response.status_code == 200
    assert response.text

    response_text = json.loads(response.text)
    assert "reply" in response_text
    assert response_text["reply"]

    if expected_text:
        assert response_text["reply"] == expected_text


def check_bad_request(client, body, headers=None, expected_status_code=400):
    if headers is None:
        headers = {"content-type": "application/json"}
    response = client.simulate_post(QUERY_ENDPOINT, json=body, headers=headers)
    assert response
    assert response.status_code == expected_status_code


def test_health_endpoint(client):
    response = client.simulate_get(HEALTH_ENDPOINT)

    assert response
    assert response.status_code == 200


def test_post_words(client, body):
    check_response(client, body)


def test_post_empty(client, body):
    body["text"] = ""
    check_response(client, body, expected_text=MarkovifyAdapter.DEFAULT_RESPONSE)


def test_invalid_body_missing_text(client, body):
    del body["text"]
    check_bad_request(client, body)


def test_invalid_body_missing_channel(client, body):
    del body["channel"]
    check_bad_request(client, body)


def test_empty_body(client):
    check_bad_request(client, {})


def test_unknown_channel(client, body):
    body["channel"] = "##something-something"
    check_bad_request(client, body, expected_status_code=403)

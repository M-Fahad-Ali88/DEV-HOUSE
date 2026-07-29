from unittest.mock import Mock, patch
import requests
import pytest


# External Webhook Service
class WebhookService:

    def send_webhook(self, url, data):
        response = requests.post(url, json=data)

        if response.status_code == 200:
            return "Webhook Sent"

        return "Webhook Failed"


# Test Successful Webhook
@patch("requests.post")
def test_webhook_success(mock_post):

    # Fake response
    mock_response = Mock()
    mock_response.status_code = 200

    # Return fake response
    mock_post.return_value = mock_response

    service = WebhookService()

    result = service.send_webhook(
        "https://example.com/webhook",
        {"event": "payment"}
    )

    assert result == "Webhook Sent"

    # Verify API call
    mock_post.assert_called_once_with(
        "https://example.com/webhook",
        json={"event": "payment"}
    )


# Test Failed Webhook
@patch("requests.post")
def test_webhook_failure(mock_post):

    mock_response = Mock()
    mock_response.status_code = 500

    mock_post.return_value = mock_response

    service = WebhookService()

    result = service.send_webhook(
        "https://example.com/webhook",
        {"event": "payment"}
    )

    assert result == "Webhook Failed"


# Test Network Error
@patch("requests.post")
def test_webhook_exception(mock_post):

    mock_post.side_effect = Exception("Network Error")

    service = WebhookService()

    with pytest.raises(Exception):
        service.send_webhook(
            "https://example.com/webhook",
            {"event": "payment"}
        )
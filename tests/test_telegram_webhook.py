import json

import pytest

from apps.notifications.telegram.client import TelegramClient

URL = "/telegram/webhook/"
SECRET_HEADER = "HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN"


@pytest.fixture
def telegram_settings(settings):
    settings.TELEGRAM_BOT_ENABLED = True
    settings.TELEGRAM_BOT_TOKEN = "123:test"
    settings.TELEGRAM_WEBHOOK_SECRET = "s3cret-value"
    return settings


@pytest.fixture
def sent(monkeypatch):
    calls = []

    def fake_send(self, chat_id, text):
        calls.append((chat_id, text))

    monkeypatch.setattr(TelegramClient, "send_message", fake_send)
    return calls


def _post(client, body, secret="s3cret-value"):
    return client.post(
        URL,
        data=json.dumps(body),
        content_type="application/json",
        **({SECRET_HEADER: secret} if secret is not None else {}),
    )


@pytest.mark.django_db
def test_webhook_rejects_missing_or_wrong_secret(client, telegram_settings, sent):
    body = {"update_id": 1, "message": {"text": "/start", "chat": {"id": 5}}}
    assert _post(client, body, secret=None).status_code == 403
    assert _post(client, body, secret="wrong").status_code == 403
    assert sent == []


@pytest.mark.django_db
def test_webhook_rejects_get(client, telegram_settings):
    assert client.get(URL).status_code == 405


@pytest.mark.django_db
def test_webhook_rejects_invalid_json(client, telegram_settings):
    response = client.post(
        URL, data="{not json", content_type="application/json", **{SECRET_HEADER: "s3cret-value"}
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_webhook_replies_to_plain_start(client, telegram_settings, sent):
    body = {"update_id": 2, "message": {"text": "/start", "chat": {"id": 77}}}
    response = _post(client, body)
    assert response.status_code == 200
    assert len(sent) == 1
    assert sent[0][0] == "77"


@pytest.mark.django_db
def test_webhook_ignores_unrelated_messages(client, telegram_settings, sent):
    body = {"update_id": 3, "message": {"text": "salom", "chat": {"id": 77}}}
    assert _post(client, body).status_code == 200
    assert sent == []


@pytest.mark.django_db
def test_webhook_503_when_telegram_disabled(client, telegram_settings, settings, sent):
    settings.TELEGRAM_BOT_ENABLED = False
    body = {"update_id": 4, "message": {"text": "/start", "chat": {"id": 77}}}
    assert _post(client, body).status_code == 503
    assert sent == []

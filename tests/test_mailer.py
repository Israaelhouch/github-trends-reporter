import smtplib

import pytest

from src import config
from src.notifier import mailer


class FakeSMTP:
    login_error = None

    def __init__(self, *args, **kwargs):
        self.sent = []

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        pass

    def login(self, user, password):
        if self.login_error:
            raise self.login_error

    def send_message(self, msg):
        self.sent.append(msg)


@pytest.fixture(autouse=True)
def email_settings(monkeypatch):
    monkeypatch.setattr(config, "EMAIL_USER", "me@gmail.com")
    monkeypatch.setattr(config, "EMAIL_PASS", "apppassword")
    monkeypatch.setattr(config, "EMAIL_RECEIVER", "you@example.com")
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    FakeSMTP.login_error = None


def test_sends_successfully():
    mailer.send_email("subject", "text", "<p>html</p>")


@pytest.mark.parametrize(
    "error",
    [smtplib.SMTPServerDisconnected("Connection unexpectedly closed"), smtplib.SMTPAuthenticationError(535, b"bad")],
)
def test_login_failures_raise_clear_error(error):
    # Regression: Gmail dropping the connection at AUTH used to surface as a raw traceback.
    FakeSMTP.login_error = error
    with pytest.raises(mailer.EmailError, match="App Password"):
        mailer.send_email("subject", "text")

import os

import pytest
from flask import Flask

from usmgpm.app import init_app


username = os.environ.get('TEST_USERNAME')
password = os.environ.get('TEST_PASSWORD')

admin_username = os.environ.get('TEST_ADMINNAME')
admin_password = os.environ.get('TEST_ADMINPASS')


@pytest.fixture()
def app():
    return init_app(testing=True)


def test_send(app: Flask):
    from usmgpm.services.email import EmailService

    with app.app_context():
        service = EmailService()
        service.send('test@mail.com', 'Subject', 'Content')


def test_send_bulk(app: Flask):
    from usmgpm.services.email import EmailService

    with app.app_context():
        service = EmailService()
        n = 10
        recipients = [f'test_{i}@test.com' for i in range(n)]
        content = 'Greetings %s, you\'re the recipient number %d'
        fills = [(f'test_{i}', i) for i in range(n)]

        count = 0
        for msg in service.send_bulk(recipients, 'Subject', content, fills):
            assert msg == f'Greetings test_{count}, you\'re the recipient number {count}'
            count += 1

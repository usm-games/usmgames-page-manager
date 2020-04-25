from tests import client


def test_empty_db(client):
    rv = client.get('/')

    assert rv.data == b'Hello World!'

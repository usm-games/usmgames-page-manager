import os
from usmgpm.services.wordpress import WordPressService

username = os.environ.get('TEST_USERNAME')
password = os.environ.get('TEST_PASSWORD')

admin_username = os.environ.get('TEST_ADMINNAME')
admin_password = os.environ.get('TEST_ADMINPASS')


def test_login():
    service = WordPressService()
    auth = service.login(username, password)
    user_data = service.get('wp/v2/users/me')
    assert user_data['name'] == auth.display_name

    auth = service.login(admin_username, admin_password)
    user_data = service.get('wp/v2/users/me')
    assert user_data['name'] == auth.display_name

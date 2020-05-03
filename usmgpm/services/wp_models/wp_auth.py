

class WPAuth:
    username: str
    email: str
    display_name: str
    token: str

    def __init__(self, username: str, email: str, display_name: str, token: str):
        self.username = username
        self.email = email
        self.display_name = display_name
        self.token = token

    @staticmethod
    def from_json(user_data: dict):
        return WPAuth(
            username=user_data['user_nicename'],
            email=user_data['user_email'],
            display_name=user_data['user_display_name'],
            token=user_data['token']
        )

    def __str__(self):
        return f"WPAuth(username={self.username}, email={self.email}, display_name={self.display_name})"

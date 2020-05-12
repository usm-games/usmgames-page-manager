from typing import List, Tuple

from flask import current_app
from flask_mail import Mail, Message, Connection


class EmailService:
    mail: Mail

    def __init__(self):
        self.mail = Mail(current_app)

    @property
    def is_active(self):
        return True

    def send(self, recipient: str, subject: str, content: str):
        msg = Message(recipients=[recipient], body=content, subject=subject)
        self.mail.send(msg)

    def send_bulk(self, recipients: List[str], subject: str, content: str, fills: List[Tuple] = None):
        if fills is not None:
            assert len(recipients) == len(fills)

        with self.mail.connect() as conn:
            for recip_idx in range(len(recipients)):
                recipient = recipients[recip_idx]
                if fills is not None:
                    fill = fills[recip_idx]
                    message = content % fill
                else:
                    message = content
                msg = Message(recipients=[recipient], body=message, subject=subject)
                conn.send(msg)
                yield message

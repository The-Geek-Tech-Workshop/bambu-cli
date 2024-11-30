from dataclasses import dataclass


@dataclass
class Account:
    email: str
    access_token: str
    refresh_token: str
    user_id: str

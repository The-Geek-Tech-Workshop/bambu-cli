from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Account:
    email: str
    access_token: str
    refresh_token: str
    user_id: str
    token_expires_at: Optional[datetime] = None


from datetime import datetime, timedelta
from typing import Optional

from bambucli.bambu.account import Account
from bambucli.bambu.httpapi import refresh_token
from bambucli.config import add_cloud_account, get_cloud_account

TOKEN_REFRESH_THRESHOLD = timedelta(days=28)


def get_account_and_ensure_token(email: Optional[str] = None) -> Account:
    """Get the account from the config file and ensure that the token is not too close to expiry.

    Parameters:
        email: Email address of the account to get (None to get the default account)

    Returns:
        account: Account object
    """
    account = get_cloud_account(email)
    # refresh token endpoint always returns 401 now
    # if account.token_expires_at is None or datetime.now() - account.token_expires_at <= TOKEN_REFRESH_THRESHOLD:
    #     account = refresh_token(account)
    #     add_cloud_account(account)
    return account

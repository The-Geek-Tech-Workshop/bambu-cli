from abc import ABC
import dataclasses
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Union
from bambucli.bambu.account import Account
from bambucli.bambu.printer import Printer, PrinterModel
from bambucli.bambu.project import Project
import cloudscraper
import certifi
from requests.exceptions import HTTPError
from dataclasses import dataclass

# Many thanks to https://github.com/t0nyz0/bambu-auth/blob/main/auth.py for working the login parts out :)

# Slicer headers
headers = {
    'User-Agent': 'bambu_network_agent/01.09.05.01',
    'X-BBL-Client-Name': 'OrcaSlicer',
    'X-BBL-Client-Type': 'slicer',
    'X-BBL-Client-Version': '01.09.05.51',
    'X-BBL-Language': 'en-US',
    'X-BBL-OS-Type': 'linux',
    'X-BBL-OS-Version': '6.2.0',
    'X-BBL-Agent-Version': '01.09.05.01',
    'X-BBL-Executable-info': '{}',
    'X-BBL-Agent-OS-Type': 'linux',
    'accept': 'application/json',
    'Content-Type': 'application/json'
}


class LOGIN_STATUS(ABC):
    pass


@dataclass
class LOGIN_SUCCESS(LOGIN_STATUS):
    access_token: str
    refresh_token: str


@dataclass
class LOGIN_VERIFICATION_CODE_REQUIRED(LOGIN_STATUS):
    pass


@dataclass
class LOGIN_MFA_REQUIRED(LOGIN_STATUS):
    tfa_key: str


BAMBU_API_BASE = "https://api.bambulab.com"


class URLS(Enum):
    LOGIN = f"{BAMBU_API_BASE}/v1/user-service/user/login"
    REQUEST_EMAIL_CODE = f"{
        BAMBU_API_BASE}/v1/user-service/user/sendemail/code"
    TFA = "https://bambulab.com/api/sign-in/tfa"
    REFRESH_TOKEN = f"{BAMBU_API_BASE}/v1/user-service/user/refreshtoken"
    GET_PROJECTS = f"{BAMBU_API_BASE}/v1/iot-service/api/user/project"
    GET_PROJECT = f"{BAMBU_API_BASE}/v1/iot-service/api/user/project/%s"
    GET_PRINTERS = f"{BAMBU_API_BASE}/v1/iot-service/api/user/bind"


_client = cloudscraper.create_scraper(browser={'custom': 'chrome'})


def login_with_email_and_password(email, password) -> LOGIN_STATUS:
    auth_response = _post(
        URLS.LOGIN.value,
        json={
            "account": email,
            "password": password,
            "apiError": ""
        }
    )
    if auth_response.text.strip() == "":
        raise ValueError(
            "Empty response from server, possible Cloudflare block.")
    auth_json = auth_response.json()

    # If login is successful
    if auth_json.get("success"):
        return LOGIN_SUCCESS(
            access_token=auth_json.get("accessToken"),
            refresh_token=auth_json.get("refreshToken")
        )

    # Handle additional authentication scenarios
    login_type = auth_json.get("loginType")
    if login_type == "verifyCode":
        return LOGIN_VERIFICATION_CODE_REQUIRED()
    elif login_type == "tfa":
        return LOGIN_MFA_REQUIRED(tfa_key=auth_json.get("tfaKey"))
    else:
        raise ValueError(f"Unknown login type: {login_type}")


def request_verification_code(email):
    _post(
        URLS.REQUEST_EMAIL_CODE.value,
        json={
            "email": email,
            "type": "codeLogin"
        }
    )


def login_with_verification_code(email, code) -> LOGIN_SUCCESS:
    verify_response = _post(
        URLS.LOGIN.value,
        json={
            "account": email,
            "code": code
        }
    )
    if verify_response.text.strip() == "":
        raise ValueError(
            "Empty response from server during verification, possible Cloudflare block.")
    json_response = verify_response.json()
    return LOGIN_SUCCESS(access_token=json_response.get("accessToken"), refresh_token=json_response.get("refreshToken"))


def login_with_mfa(tfa_key, tfa_code) -> LOGIN_SUCCESS:
    tfa_response = _post(
        URLS.TFA.value,
        json={
            "tfaKey": tfa_key,
            "tfaCode": tfa_code
        }
    )
    if tfa_response.text.strip() == "":
        raise ValueError(
            "Empty response from server during MFA, possible Cloudflare block.")
    cookies = tfa_response.cookies.get_dict()
    return LOGIN_SUCCESS(cookies.get("token"), cookies.get("refreshToken"))


def complete_account(email: str, access_token: str, refresh_token: str) -> Account:
    return Account(
        email=email,
        access_token=access_token,
        refresh_token=refresh_token,
        user_id=get_projects(access_token)[0].user_id
    )


def refresh_token(account: Account) -> Account:
    """
    This endpoint only returns 401 responses now, kept for completion

    Refresh the access token for the account
    """
    json = _post(URLS.REFRESH_TOKEN.value, json={
        "refreshToken": account.refresh_token
    }).json()
    expires_at = datetime.now() + timedelta(seconds=float(json.get("expiresIn")))
    return dataclasses.replace(account, access_token=json.get("accessToken"), refresh_token=json.get("refreshToken"), token_expires_at=expires_at)


def get_projects(account: Union[str, Account]) -> List[Project]:
    api_response = _authorised_get(
        URLS.GET_PROJECTS.value, account.access_token if isinstance(account, Account) else account)
    json = api_response.json()
    return list(map(lambda project: Project.from_json(project), json.get("projects", [])))


def get_project(account: Account, project_id: str) -> Project:
    api_response = _authorised_get(
        URLS.GET_PROJECT.value % project_id, account.access_token)
    json = api_response.json()
    return Project.from_json(json)


def get_printers(account: Account) -> List[Printer]:
    api_response = _authorised_get(
        URLS.GET_PRINTERS.value, account.access_token)
    json = api_response.json()

    return list(map(lambda printer: Printer(
        serial_number=printer.get("dev_id"),
        name=printer.get("name"),
        access_code=printer.get("dev_access_code"),
        model=PrinterModel.from_model_code(
            printer.get("dev_model_name")),
        account_email=account.email,
        ip_address=None
    ), json.get("devices", [])))


def _authorised_get(url, access_token):
    return _get(
        url,
        headers=dict(
            headers, **{"Authorization": f"Bearer {access_token}"}),
    )


def _get(url, headers=headers):
    response = _client.get(
        url,
        headers=headers,
        verify=certifi.where()
    )
    response.raise_for_status()  # Raise an exception if the request fails
    return response


def _authorised_post(url, access_token, json=None):
    return _post(
        url,
        headers=dict(
            headers, **{"Authorization": f"Bearer {access_token}"}),
        json=json
    )


def _post(url, headers=headers, json=None):
    response = _client.post(
        url,
        headers=headers,
        json=json,
        verify=certifi.where()
    )
    response.raise_for_status()  # Raise an exception if the request fails
    return response

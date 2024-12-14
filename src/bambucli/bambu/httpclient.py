
from abc import ABC
from bambucli.bambu.printer import Printer, PrinterModel
from bambucli.bambu.project import Project
import cloudscraper
import certifi
from requests.exceptions import HTTPError
from dataclasses import dataclass

# Many thanks to https://github.com/t0nyz0/bambu-auth/blob/main/auth.py for working this out :)

BAMBU_LOGIN_HOST = "api.bambulab.com"
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


class HttpClient:
    def __init__(self):
        self._client = cloudscraper.create_scraper(
            browser={'custom': 'chrome'})

    def login_with_email_and_password(self, email, password) -> LOGIN_STATUS:
        auth_payload = {
            "account": email,
            "password": password,
            "apiError": ""
        }

        auth_response = self._client.post(
            f"https://{BAMBU_LOGIN_HOST}/v1/user-service/user/login",
            headers=headers,
            json=auth_payload,
            verify=certifi.where()
        )
        auth_response.raise_for_status()
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

    def request_verification_code(self, email):
        send_code_response = self._client.post(
            f"https://{BAMBU_LOGIN_HOST}/v1/user-service/user/sendemail/code",
            headers=headers,
            json={
                "email": email,
                "type": "codeLogin"
            },
            verify=certifi.where()
        )
        send_code_response.raise_for_status()

    def login_with_verification_code(self, email, code):
        verify_response = self._client.post(
            f"https://{BAMBU_LOGIN_HOST}/v1/user-service/user/login",
            headers=headers,
            json={
                "account": email,
                "code": code
            },
            verify=certifi.where()
        )
        verify_response.raise_for_status()
        if verify_response.text.strip() == "":
            raise ValueError(
                "Empty response from server during verification, possible Cloudflare block.")
        json_response = verify_response.json()
        return LOGIN_SUCCESS(access_token=json_response.get("accessToken"), refresh_token=json_response.get("refreshToken"))

    def login_with_mfa(self, tfa_key, tfa_code):
        verify_payload = {
            "tfaKey": tfa_key,
            "tfaCode": tfa_code
        }

        tfa_response = self._client.post(
            "https://bambulab.com/api/sign-in/tfa",
            headers=headers,
            json=verify_payload,
            verify=certifi.where()
        )
        tfa_response.raise_for_status()
        if tfa_response.text.strip() == "":
            raise ValueError(
                "Empty response from server during MFA, possible Cloudflare block.")
        cookies = tfa_response.cookies.get_dict()
        return LOGIN_SUCCESS(cookies.get("token"), cookies.get("refreshToken"))

    def get_projects(self, access_token):
        try:
            api_response = self._client.get(
                f"https://{BAMBU_LOGIN_HOST}/v1/iot-service/api/user/project",
                headers=dict(
                    headers, **{"Authorization": f"Bearer {access_token}"}),
                verify=certifi.where()
            )

            json = api_response.json()
            return list(map(lambda project: Project.from_json(project), json.get("projects", [])))

        except HTTPError as http_err:
            print(f"HTTP error occurred during API request: {http_err}")

    def get_project(self, account, project_id):
        try:
            api_response = self._client.get(
                f"https://{BAMBU_LOGIN_HOST}/v1/iot-service/api/user/project/{project_id}",
                headers=dict(
                    headers, **{"Authorization": f"Bearer {account.access_token}"}),
                verify=certifi.where()
            )

            json = api_response.json()
            print(api_response.text)
            return Project.from_json(json)

        except HTTPError as http_err:
            print(f"HTTP error occurred during API request: {http_err}")

    def get_printers(self, account):
        try:
            api_response = self._client.get(
                f"https://{BAMBU_LOGIN_HOST}/v1/iot-service/api/user/bind",
                headers=dict(
                    headers, **{"Authorization": f"Bearer {account.access_token}"}),
                verify=certifi.where()
            )

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

        except HTTPError as http_err:
            print(f"HTTP error occurred during API request: {http_err}")


import json
from bambucli.bambu.printer import Printer, PrinterModel
from bambucli.bambu.project import Project
import cloudscraper
import certifi
from requests.exceptions import HTTPError

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


class HttpClient:
    def __init__(self):
        self._client = cloudscraper.create_scraper(
            browser={'custom': 'chrome'})

    def get_auth_tokens(self, email, password):
        auth_payload = {
            "account": email,
            "password": password,
            "apiError": ""
        }

        try:
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
                return auth_json.get("accessToken"), auth_json.get("refreshToken")

            # Handle additional authentication scenarios
            login_type = auth_json.get("loginType")
            if login_type == "verifyCode":
                return self._handle_verification_code(email)
            elif login_type == "tfa":
                return self._handle_mfa(auth_json.get("tfaKey"))
            else:
                raise ValueError(f"Unknown login type: {login_type}")

        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except json.JSONDecodeError as json_err:
            print(f"JSON decode error: {
                json_err}. Response content: {auth_response.text}")
        except Exception as err:
            print(f"Other error occurred: {err}")
        return None, None

        # print(f"Access token: {access_token}")
        # print(f"Refresh token: {refresh_token}")

    def _handle_verification_code(self, email):
        send_code_payload = {
            "email": email,
            "type": "codeLogin"
        }

        try:
            send_code_response = self._client.post(
                f"https://{BAMBU_LOGIN_HOST}/v1/user-service/user/sendemail/code",
                headers=headers,
                json=send_code_payload,
                verify=certifi.where()
            )
            send_code_response.raise_for_status()
            print("Verification code sent successfully. Please check your email.")
            verify_code = input("Enter your access code: ")

            verify_payload = {
                "account": email,
                "code": verify_code
            }
            verify_response = self._client.post(
                f"https://{BAMBU_LOGIN_HOST}/v1/user-service/user/login",
                headers=headers,
                json=verify_payload,
                verify=certifi.where()
            )
            verify_response.raise_for_status()
            if verify_response.text.strip() == "":
                raise ValueError(
                    "Empty response from server during verification, possible Cloudflare block.")
            json_response = verify_response.json()
            return json_response.get("accessToken"), json_response.get("refreshToken")

        except HTTPError as http_err:
            print(f"HTTP error occurred during verification: {http_err}")
        except json.JSONDecodeError as json_err:
            print(f"JSON decode error during verification: {
                json_err}. Response content: {verify_response.text}")
        except Exception as err:
            print(f"Other error occurred during verification: {err}")
        return None, None

    def _handle_mfa(self, tfa_key):
        tfa_code = input("Enter your MFA access code: ")
        verify_payload = {
            "tfaKey": tfa_key,
            "tfaCode": tfa_code
        }

        try:
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
            return cookies.get("token"), cookies.get("refreshToken")

        except HTTPError as http_err:
            print(f"HTTP error occurred during MFA: {http_err}")
        except json.JSONDecodeError as json_err:
            print(f"JSON decode error during MFA: {
                json_err}. Response content: {tfa_response.text}")
        except Exception as err:
            print(f"Other error occurred during MFA: {err}")
        return None, None

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

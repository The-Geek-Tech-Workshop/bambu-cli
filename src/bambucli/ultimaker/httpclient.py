import asyncio
from dataclasses import dataclass
from enum import Enum
from typing import Union
from bambucli.bambu.printer import Printer
from bambucli.ultimaker.printer import LoginDetails, UltimakerPrinter
from bambucli.ultimaker.system_info import SystemInfo
import requests
from requests.auth import HTTPDigestAuth


APPLICATION_NAME = 'BambuCli'
USER_NAME = 'bambu-cli'
EXCLUSION_KEY = 'bambu-cli'


class URLS(Enum):
    REQUEST_AUTH = 'http://%s/api/v1/auth/request'
    CHECK_FOR_AUTH_CONFIRMATION = 'http://%s/api/v1/auth/check/%s'
    VERIFY_AUTH = 'http://%s/api/v1/auth/verify'
    GET_SYSTEM_INFO = 'http://%s/api/v1/system'


def request_login_details(ip_address: str) -> LoginDetails:
    print(URLS.REQUEST_AUTH.value % ip_address)
    response = requests.post(URLS.REQUEST_AUTH.value % ip_address, data={
        'application': APPLICATION_NAME,
        'user': USER_NAME,
        'exclusion_key': EXCLUSION_KEY
    })
    response.raise_for_status()
    auth_details = response.json()
    return LoginDetails(id=auth_details.get('id'), key=auth_details.get('key'))


def wait_for_authorisation(ip_address: str, login_details: LoginDetails) -> bool:
    async def check_auth(id):
        auth_result = None
        while auth_result is None:
            response = requests.get(
                URLS.CHECK_FOR_AUTH_CONFIRMATION.value % (ip_address, id)).json()
            if response['message'] == 'authorized':
                auth_result = True
            elif response['message'] == 'unauthorized':
                auth_result = False
            elif response['message'] == 'unknown':
                auth_result = None
            else:
                raise ValueError(f'Unknown auth response: {response}')
            await asyncio.sleep(1)
        return auth_result

    loop = asyncio.get_event_loop()
    task = loop.create_task(check_auth(login_details.id))
    return loop.run_until_complete(task)


def verify_login_details(ip_address: str, login_details: LoginDetails) -> bool:
    response = requests.get(URLS.VERIFY_AUTH.value % ip_address, auth=HTTPDigestAuth(
        login_details.id, login_details.key
    ))
    response.raise_for_status()
    return response.json().get('message') == 'ok'


def get_system_info(printer: Union[str, UltimakerPrinter]) -> SystemInfo:
    ip_address = printer.ip_address if isinstance(
        printer, Printer) else printer
    response = requests.get(URLS.GET_SYSTEM_INFO.value % ip_address)
    response.raise_for_status()
    return SystemInfo.from_json(response.json())

import json
import requests

BAMBU_LOGIN_HOST = "api.bambulab.com"


def login(args):
    # Can't do this as have been blocked :/
    # response = requests.post(
    #     f"https://{BAMBU_LOGIN_HOST}/v1/user-service/user/login",
    #     headers={'Content-Type': 'application/json'},
    #     data=json.dumps({
    #         "account": args.email,
    #         "password": args.password,
    #     }))
    # access_token = response.json().get('access_token')
    # refresh_token = response.json().get('refresh_token')

    refresh_token = args.refresh_token
    response = requests.post(
        f"https://{BAMBU_LOGIN_HOST}/v1/user-service/user/refreshtoken",
        headers={'Content-Type': 'application/json'},
        data=json.dumps({
            "refreshToken": refresh_token,
        }))
    print(response.status_code)
    print(response.json())
    access_token = response.json().get('access_token')
    new_refresh_token = response.json().get('refresh_token')
    print(f"Access token: {access_token}")
    print(f"Refresh token: {new_refresh_token}")

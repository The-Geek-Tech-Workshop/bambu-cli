from bambucli.bambu.account import Account
from bambucli.bambu.httpclient import HttpClient
from bambucli.config import add_cloud_account


def login(args):

    email = args.email
    password = args.password if args.password else input("Password: ")

    client = HttpClient()
    access_token, refresh_token = client.get_auth_tokens(
        email, password)

    user_id = client.get_projects(access_token)[0].user_id

    add_cloud_account(
        Account(args.email, access_token, refresh_token, user_id))

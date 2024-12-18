from bambucli.bambu.account import Account
from bambucli.bambu.httpapi import LOGIN_MFA_REQUIRED, LOGIN_SUCCESS, LOGIN_VERIFICATION_CODE_REQUIRED, complete_account, get_projects, login_with_email_and_password, login_with_mfa, login_with_verification_code, request_verification_code
from bambucli.config import add_cloud_account
from bambucli.spinner import Spinner


def login(args):

    spinner = Spinner()

    email = args.email
    password = args.password if args.password else input("Password: ")

    spinner.task_in_progress("Logging in to Bambu Cloud")
    response = login_with_email_and_password(email, password)
    spinner.task_complete()

    def store_tokens(access_token, refresh_token):
        spinner.task_in_progress("Fetching account user ID")
        account = complete_account(email, access_token, refresh_token)
        spinner.task_complete()

        spinner.task_in_progress(
            "Saving account details", lambda: add_cloud_account(account))

    try:
        match response:
            case LOGIN_SUCCESS(access_token, refresh_token):
                store_tokens(access_token, refresh_token)
            case LOGIN_VERIFICATION_CODE_REQUIRED():
                request_verification_code(email)
                print("Verification code has been sent to your email.")
                verification_code = input("Verification code: ")
                spinner.task_in_progress("Logging in with verification code")
                response = login_with_verification_code(
                    email, verification_code)
                spinner.task_complete()
                spinner.task_in_progress("Saving account details")
                store_tokens(response.access_token, response.refresh_token)
                spinner.task_complete()
            case LOGIN_MFA_REQUIRED(tfa_key):
                tfa_code = input("Enter your MFA access code: ")
                spinner.task_in_progress("Logging in with MFA code")
                response = login_with_mfa(email, tfa_key, tfa_code)
                store_tokens(response.access_token, response.refresh_token)
    except Exception as e:
        spinner.task_failed(e)
        return

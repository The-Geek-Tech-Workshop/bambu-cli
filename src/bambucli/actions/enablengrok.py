from bambucli.config import set_ngrok_auth_token
from bambucli.spinner import Spinner


def enable_ngrok(args):
    spinner = Spinner()
    spinner.task_in_progress("Saving ngrok auth token",
                             lambda: set_ngrok_auth_token(args.auth_token))

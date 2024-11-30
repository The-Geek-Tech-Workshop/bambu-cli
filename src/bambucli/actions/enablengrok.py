from bambucli.config import set_ngrok_auth_token


def enable_ngrok(args):
    set_ngrok_auth_token(args.auth_token)

from bambucli.bambu.account import Account
from bambucli.bambu.printer import Printer, PrinterModel
import json
from pathlib import Path
import logging
from typing import Optional, Dict


def get_printer(name: str) -> Optional[Printer]:
    """Read printer configuration from JSON file."""
    try:
        config_file = Path.home() / '.bambu-cli' / 'printers.json'

        if not config_file.exists():
            logging.error("No printer configuration file found")
            return None

        with open(config_file, 'r') as f:
            config = json.load(f)

        if (name not in config):
            logging.error(f"Printer {name} not found in configuration")
            return None

        return deserialise_printer(config[name])

    except Exception as e:
        logging.error(f"Failed to load printer configuration: {e}")
        return None


def add_printer(printer: Printer) -> bool:
    try:

        # Setup config directory
        config_dir = Path.home() / '.bambu-cli'
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / 'printers.json'

        # Load existing config
        config = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)

        # Update config
        name = printer.id()
        config[name] = serialise_printer(printer)

        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        logging.info(f"Printer {name} configuration saved")
        return True

    except Exception as e:
        logging.error(f"Failed to save printer configuration: {e}")
        return False


def serialise_printer(printer: Printer) -> Dict:
    return {
        'ip_address': printer.ip_address,
        'serial_number': printer.serial_number,
        'name': printer.name,
        'access_code': printer.access_code,
        'model': printer.model.value,
        'account_email': printer.account_email
    }


def deserialise_printer(printer_config: Dict) -> Optional[Printer]:
    return Printer(
        ip_address=printer_config['ip_address'],
        serial_number=printer_config['serial_number'],
        name=printer_config['name'],
        access_code=printer_config['access_code'],
        model=PrinterModel(printer_config['model']),
        account_email=printer_config['account_email']
    )


def add_cloud_account(account: Account) -> bool:
    try:

        # Setup config directory
        config_dir = Path.home() / '.bambu-cli'
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / 'accounts.json'

        # Load existing config
        config = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)

        # Create printer entry
        auth_token_config = {
            'email': account.email,
            'access_token': account.access_token,
            'refresh_token': account.refresh_token,
            'user_id': account.user_id
        }

        # Update config
        config[account.email] = auth_token_config

        # Set default if this is the only entry
        if len(config) == 1:
            config['default'] = account.email

        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        logging.info(f"Account data for {account.email} saved")
        return True

    except Exception as e:
        logging.error(f"Failed to save account data: {e}")
        return False


def get_cloud_account(email: Optional[str] = None):
    try:
        config_file = Path.home() / '.bambu-cli' / 'accounts.json'

        if not config_file.exists():
            logging.error("No account configuration file found")
            return None

        with open(config_file, 'r') as f:
            config = json.load(f)

        if email is None:
            email = config.get('default', None)

        if email not in config:
            logging.error(f"Account {email} not found in configuration")
            return None

        account_config = config[email]

        return Account(
            email=account_config['email'],
            access_token=account_config['access_token'],
            refresh_token=account_config['refresh_token'],
            user_id=account_config['user_id']
        )

    except Exception as e:
        logging.error(f"Failed to load account configuration: {e}")
        return None


def set_ngrok_auth_token(ngrok_auth_token: str) -> bool:
    try:

        # Setup config directory
        config_dir = Path.home() / '.bambu-cli'
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / 'ngrok.json'

        # Update config
        config = {
            'auth_token': ngrok_auth_token
        }

        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        logging.info(f"Ngrok auth token saved")
        return True

    except Exception as e:
        logging.error(f"Failed to save ngrok auth token: {e}")
        return False


def get_ngrok_auth_token() -> Optional[str]:
    try:
        config_file = Path.home() / '.bambu-cli' / 'ngrok.json'

        if not config_file.exists():
            logging.error("No ngrok configuration file found")
            return None

        with open(config_file, 'r') as f:
            config = json.load(f)

        return config.get('auth_token', None)

    except Exception as e:
        logging.error(f"Failed to load ngrok auth token: {e}")
        return None

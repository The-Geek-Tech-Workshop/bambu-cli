from bambu.printer import LocalPrinter, Printer
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

        printer_config = config[name]
        return LocalPrinter(
            ip_address=printer_config['ip_address'],
            access_code=printer_config['access_code'],
            serial_number=printer_config['serial_number'],
            name=name
        )

    except Exception as e:
        logging.error(f"Failed to load printer configuration: {e}")
        return None


def get_all_printers() -> Dict[str, Printer]:
    """Read all printer configurations from JSON file."""
    try:
        config_file = Path.home() / '.bambu-cli' / 'printers.json'

        if not config_file.exists():
            return {}

        with open(config_file, 'r') as f:
            config = json.load(f)

        return {
            serial: LocalPrinter(**printer_config)
            for serial, printer_config in config.items()
        }

    except Exception as e:
        logging.error(f"Failed to load printer configurations: {e}")
        return {}


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

        # Create printer entry
        printer_config = {
            'ip_address': printer.ip_address,
            'access_code': printer.access_code,
            'serial_number': printer.serial_number
        }

        # Update config
        name = printer.name if hasattr(
            printer, 'name') and printer.name is not None else printer.serial_number
        config[name] = printer_config

        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

        logging.info(f"Printer {name} configuration saved")
        return True

    except Exception as e:
        logging.error(f"Failed to save printer configuration: {e}")
        return False

import logging
from bambucli.bambu.printer import LocalPrinter
from bambucli.config import add_printer as add_printer_to_config

logger = logging.getLogger(__name__)


def add_printer(args) -> bool:
    """
    Save printer configuration to JSON file.

    Args:
        args: Namespace containing:
            - ip: Printer IP address
            - access_code: Printer access code
            - serial: Printer serial number
            - name: Optional friendly name

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Validate required args
        required = ['ip', 'access_code', 'serial']
        if not all(hasattr(args, attr) for attr in required):
            logging.error("Missing required parameters")
            return False

        return add_printer_to_config(LocalPrinter(
            ip_address=args.ip,
            access_code=args.access_code,
            serial_number=args.serial,
            name=args.name
        ))

    except Exception as e:
        logger.error(f"Failed to save printer configuration: {e}")
        return False

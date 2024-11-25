import logging
from bambucli.bambu.mqttclient import MqttClient
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

    """
    # Validate required args
    required = ['ip', 'access_code', 'serial']
    if not all(hasattr(args, attr) for attr in required):
        logging.error("Missing required parameters")
        return

    def on_connect(client, reason_code):
        client.get_version_info()

    def on_get_version(client, message):
        try:
            add_printer_to_config(LocalPrinter(
                ip_address=args.ip,
                access_code=args.access_code,
                serial_number=args.serial,
                model=message.get_printer_model(),
                name=args.name
            ))
        except Exception as e:
            logger.error(f"Failed to save printer configuration: {e}")

        client.disconnect()

    bambuMqttClient = MqttClient.for_local_printer(
        ip_address=args.ip,
        serial_number=args.serial,
        access_code=args.access_code,
        on_connect=on_connect,
        on_get_version=on_get_version)

    bambuMqttClient.connect()
    bambuMqttClient.loop_forever()

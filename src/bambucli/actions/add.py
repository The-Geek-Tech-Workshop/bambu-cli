import logging
from time import sleep
from bambucli.bambu.mqttclient import MqttClient
from bambucli.bambu.printer import LocalPrinter
from bambucli.config import add_printer as add_printer_to_config
from bambucli.spinner import Spinner
from rich.console import Console

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

    with Spinner() as spinner:

        def on_connect(client, reason_code):
            spinner.task_complete()
            spinner.task_in_progress("Retrieving printer information")
            client.get_version_info()

        def on_get_version(client, message):
            spinner.task_complete()
            spinner.task_in_progress("Saving printer config")
            try:
                add_printer_to_config(LocalPrinter(
                    ip_address=args.ip,
                    access_code=args.access_code,
                    serial_number=args.serial,
                    model=message.printer_model(),
                    name=args.name
                ))
                spinner.task_complete()

            except Exception as e:
                logger.error(f"Failed to save printer configuration: {e}")
                spinner.task_failed()

            client.disconnect()

        bambuMqttClient = MqttClient.for_local_printer(
            ip_address=args.ip,
            serial_number=args.serial,
            access_code=args.access_code,
            on_connect=on_connect,
            on_get_version=on_get_version)

        spinner.task_in_progress(f"Connecting to printer {printer.id()}")
        bambuMqttClient.connect()
        bambuMqttClient.loop_forever()

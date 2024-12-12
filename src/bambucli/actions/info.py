from bambucli.actions.ensureip import PrinterNotFoundOnNetworkException, ensure_printer_ip_address
from bambucli.bambu.mqttclient import MqttClient
from bambucli.config import get_printer
import logging

from bambucli.spinner import Spinner

logger = logging.getLogger(__name__)


def get_version_info(args):
    spinner = Spinner()
    spinner.task_in_progress("Fetching printer details")
    printer = get_printer(args.printer)
    if printer is None:
        spinner.task_failed(f"Printer '{args.printer}' not found")
        return
    spinner.task_complete()

    if printer.ip_address is None:
        try:
            spinner.task_in_progress("Checking for printer ip address")
            printer = ensure_printer_ip_address(printer)
            spinner.task_complete()
        except PrinterNotFoundOnNetworkException as e:
            # Printer not found on network currently, but we'll allow for just this info request
            spinner.task_complete()
            pass
        except Exception as e:
            spinner.task_failed(e)
            return

    print(f"Name: {printer.name}")
    print(f"Model: {printer.model.value}")
    print(f"Serial Number: {printer.serial_number}")
    print(f"Access Code: {printer.access_code}")
    print(f"IP Address: {
          printer.ip_address if printer.ip_address else 'Unknown'}")
    print(f"Bambu Account: {
          printer.account_email if printer.account_email else 'N/A'}")

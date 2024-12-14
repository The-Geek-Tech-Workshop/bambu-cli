import dataclasses
import logging
from bambucli.bambu.mqttclient import MqttClient
from bambucli.bambu.printer import Printer
from bambucli.bambu.ssdpclient import SsdpClient
from bambucli.config import add_printer as add_printer_to_config
from bambucli.spinner import Spinner

logger = logging.getLogger(__name__)


def add_local_printer(args) -> bool:

    spinner = Spinner()
    spinner.task_in_progress("Looking for printers on local network")
    ssdpClient = SsdpClient()
    printers = ssdpClient.discover_printers()

    if len(printers) == 0:
        spinner.task_failed("No printers found")
        return

    spinner.task_complete()
    for index, printer in enumerate(printers):
        print(
            f"{index + 1}: {printer.name} - {printer.model.value} - {printer.serial_number}")
    selection = input("Select a printer: ")
    try:
        selection = int(selection)
        if selection < 1 or selection > len(printers):
            raise ValueError
        discovered_printer = printers[selection - 1]
        access_code = input("Enter the access code: ")
        printer = Printer(
            serial_number=discovered_printer.serial_number,
            name=discovered_printer.name,
            access_code=access_code,
            model=discovered_printer.model,
            account_email=None,
            ip_address=discovered_printer.ip_address
        )
        spinner.task_in_progress("Connecting to printer")

        def on_connect(client, reason_code):
            spinner.task_complete()
            spinner.task_in_progress("Saving printer config")
            try:
                # Don't store ip, we'll look it up again when we need it
                add_printer_to_config(
                    dataclasses.replace(printer, ip_address=None))
                spinner.task_complete()

            except Exception as e:
                logger.error(e)
                spinner.task_failed()

            client.disconnect()
        bambuMqttClient = MqttClient.for_printer(
            printer, on_connect=on_connect)

        bambuMqttClient.connect()
        bambuMqttClient.loop_forever()
    except ValueError:
        print("Invalid selection")
        return
    except Exception as e:
        spinner.task_failed(e)
        return

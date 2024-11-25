from bambucli.bambu.mqttclient import MqttClient
from bambucli.config import get_printer
import logging

from bambucli.spinner import Spinner

logger = logging.getLogger(__name__)


def get_version_info(args):
    printer = get_printer(args.printer)

    with Spinner() as spinner:

        def on_connect(client, reason_code):
            spinner.task_complete()
            spinner.task_in_progress("Getting version info")
            client.get_version_info()

        def on_get_version(client, message):
            spinner.task_complete()

            print(f"Model: {message.printer_model().value}")

            client.disconnect()

        bambuMqttClient = MqttClient.for_printer(
            printer,
            on_connect=on_connect,
            on_get_version=on_get_version)

        spinner.task_in_progress(f"Connecting to printer {printer.id()}")
        bambuMqttClient.connect()
        bambuMqttClient.loop_forever()

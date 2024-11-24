from bambu.mqttclient import MqttClient
from config import get_printer
import logging

logger = logging.getLogger(__name__)


def get_version_info(args):
    printer = get_printer(args.printer)

    def on_connect(client, reason_code):
        client.get_version_info()

    def on_get_version(client, message):

        p1_series_identifier = next(filter(
            lambda x: x.name == 'esp32', message.module), None)
        if p1_series_identifier:
            print(f"Model: P1 Series")
            print(f"Serial: {p1_series_identifier.sn}")
            print(f"Hardware version: {p1_series_identifier.hw_ver}")

        client.disconnect()

    bambuMqttClient = MqttClient.for_printer(
        printer,
        on_connect=on_connect,
        on_get_version=on_get_version)

    bambuMqttClient.connect()
    bambuMqttClient.loop_forever()

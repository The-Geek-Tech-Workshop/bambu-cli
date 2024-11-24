
import uuid
from bambucli.bambu.messages.getversion import GetVersionMessage
from bambucli.bambu.messages.onpushstatus import OnPushStatusMessage
from bambucli.bambu.printer import LocalPrinter, Printer
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import ssl
import logging
import json

logger = logging.getLogger(__name__)
BAMBU_LOCAL_MQTT_PORT = 8883
BAMBU_LOCAL_MQTT_USERNAME = 'bblp'

CLIENT_ID = f'bambu-cli-{str(uuid.uuid4())}'


class MqttClient:

    def for_printer(printer: Printer, on_connect=None, on_push_status=None, on_get_version=None):
        if isinstance(printer, LocalPrinter):
            return MqttClient.for_local_printer(printer.ip_address, printer.serial_number, printer.access_code, on_connect, on_push_status, on_get_version)

    def for_local_printer(ip_address: str, serial_number: str, access_code: str, on_connect=None, on_push_status=None, on_get_version=None):
        mqttClient = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311, clean_session=True, client_id=CLIENT_ID)
        mqttClient.username_pw_set(BAMBU_LOCAL_MQTT_USERNAME, access_code)
        mqttClient.tls_set(cert_reqs=ssl.CERT_NONE)
        mqttClient.tls_insecure_set(True)
        return MqttClient(mqttClient, serial_number, ip_address, BAMBU_LOCAL_MQTT_PORT, on_connect, on_push_status, on_get_version)

    def __init__(self, client, serial_number, ip_address, port, on_connect=None, on_push_status=None, on_get_version=None):
        client.on_connect = lambda _, userdata, flags, reason_code, properties: self._on_connect(
            userdata, flags, reason_code, properties)
        client.on_message = lambda client, userdata, message: self._on_message(
            message)
        self._client = client
        self._report_topic = f'device/{serial_number}/report'
        self._request_topic = f'device/{serial_number}/request'
        self.connect = lambda: self._connect(ip_address, port)
        self._custom_on_connect = on_connect
        self._on_push_status = on_push_status
        self._on_get_version = on_get_version

    def _connect(self, ip_address, port):
        self._client.connect(ip_address, port)

    def _on_connect(self, userdata, flags, reason_code, properties):
        logger.info(f'Connected with result code {str(reason_code)}')
        self._client.subscribe(self._report_topic)
        if self._on_connect:
            self._custom_on_connect(self, reason_code)

    def _on_message(self, message):
        logger.info(f'Received message {str(message.payload)}')
        json_payload = json.loads(message.payload)

        message = json_payload.get("print", json_payload.get("info"))

        match message["command"]:
            case "push_status":
                if self._on_push_status:
                    self._on_push_status(
                        self, OnPushStatusMessage.from_json(message))
            case "get_version":
                if self._on_get_version:
                    self._on_get_version(
                        self, GetVersionMessage.from_json(message))

    def loop_start(self):
        self._client.loop_start()

    def loop_stop(self):
        self._client.loop_stop()

    def loop_forever(self):
        self._client.loop_forever()

    def disconnect(self):
        self._client.disconnect()

    def _publish(self, message):
        return self._client.publish(self._request_topic, message)

    def print(self, file):
        self._publish(json.dumps(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "project_file",
                    "param": "Metadata/plate_1.gcode",
                    "project_id": "0",  # Always 0 for local prints
                    "profile_id": "0",  # Always 0 for local prints
                    "task_id": "0",  # Always 0 for local prints
                    "subtask_id": "0",  # Always 0 for local prints

                    "url": f"file:///sdcard/{file}",

                    "timelapse": False,
                    "bed_type": "auto",  # Always "auto" for local prints
                    "bed_levelling": True,
                    "flow_cali": False,
                    "vibration_cali": False,
                    "layer_inspect": False,
                    "ams_mapping": "",
                    "use_ams": False
                }
            }
        ))

    def stop_print(self):
        return self._publish(json.dumps(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "stop",
                    "param": "",
                }
            }
        ))

    def pause_print(self):
        return self._publish(json.dumps(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "pause",
                    "param": "",
                }
            }
        ))

    def resume_print(self):
        return self._publish(json.dumps(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "resume",
                    "param": "",
                }
            }
        ))

    def get_version_info(self):
        return self._publish(json.dumps(
            {
                "info": {
                    "sequence_id": "0",
                    "command": "get_version"
                }
            }
        ))

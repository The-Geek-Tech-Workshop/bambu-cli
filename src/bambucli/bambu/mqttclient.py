
from typing import Optional
import uuid
from bambucli.bambu.messages.getversion import GetVersionMessage
from bambucli.bambu.messages.onpushstatus import OnPushStatusMessage
from bambucli.bambu.printer import Printer
from bambucli.config import get_cloud_account
import paho.mqtt.client as mqtt
from paho.mqtt.enums import CallbackAPIVersion
import ssl
import logging
import json

logger = logging.getLogger(__name__)
BAMBU_CLOUD_MQTT_PORT = 8883
BAMBU_LOCAL_MQTT_PORT = 8883
BAMBU_LOCAL_MQTT_USERNAME = 'bblp'

CLIENT_ID = f'bambu-cli-{str(uuid.uuid4())}'


class ConnectionFailedException(Exception):
    def __init__(self, reason_code):
        super().__init__(
            f"Connection to printer failed with reason code: '{reason_code}'")


class MqttClient:

    def for_printer(printer: Printer, on_connect=None, on_push_status=None, on_push_full_status=None, on_get_version=None):
        if printer.account_email is not None:
            return MqttClient.for_cloud_printer(printer, on_connect, on_push_status, on_push_full_status, on_get_version)
        elif (printer.ip_address is not None):
            return MqttClient.for_local_printer(printer.ip_address, printer.serial_number, printer.access_code, on_connect, on_push_status, on_push_full_status, on_get_version)
        else:
            raise Exception(
                'Printer must have either a known IP-address or an account-email in order to connect to MQTT')

    def for_local_printer(ip_address: str, serial_number: str, access_code: str, on_connect=None, on_push_status=None, on_push_full_status=None, on_get_version=None):
        mqttClient = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311, clean_session=True, client_id=CLIENT_ID)
        mqttClient.username_pw_set(BAMBU_LOCAL_MQTT_USERNAME, access_code)
        mqttClient.tls_set(cert_reqs=ssl.CERT_NONE)
        mqttClient.tls_insecure_set(True)
        return MqttClient(mqttClient, serial_number, ip_address, BAMBU_LOCAL_MQTT_PORT, on_connect, on_push_status, on_push_full_status, on_get_version)

    def for_cloud_printer(cloud_printer, on_connect=None, on_push_status=None, on_push_full_status=None, on_get_version=None):
        account = get_cloud_account(cloud_printer.account_email)
        mqttClient = mqtt.Client(
            callback_api_version=CallbackAPIVersion.VERSION2, protocol=mqtt.MQTTv311, clean_session=True, client_id=CLIENT_ID)
        mqttClient.username_pw_set(
            f"u_{account.user_id}", account.access_token)
        mqttClient.tls_set(cert_reqs=ssl.CERT_NONE)
        mqttClient.tls_insecure_set(True)
        return MqttClient(mqttClient, cloud_printer.serial_number, 'us.mqtt.bambulab.com', BAMBU_CLOUD_MQTT_PORT, on_connect, on_push_status, on_push_full_status, on_get_version)

    def __init__(self, client, serial_number, ip_address, port, on_connect=None, on_push_status=None, on_push_full_status=None, on_get_version=None):
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
        self._on_push_full_status = on_push_full_status
        self._on_get_version = on_get_version

    def _connect(self, ip_address, port):
        self._client.connect(ip_address, port)

    def _on_connect(self, userdata, flags, reason_code, properties):
        if (reason_code == 'Success'):
            logger.info(f'Connected successfully with result code {
                        str(reason_code)}')
            self._client.subscribe(self._report_topic)
            if self._on_connect:
                self._custom_on_connect(self, reason_code)
        else:
            logger.error(f'Connection failed with result code {
                         str(reason_code)}')
            raise ConnectionFailedException(reason_code)

    def _on_message(self, message):
        logger.info(f'Received message {str(message.payload)}')
        json_payload = json.loads(message.payload)

        message = json_payload.get("print", json_payload.get("info"))

        if message is not None:
            match message.get("command", ""):
                case "push_status":
                    if self._on_push_full_status or self._on_push_status:
                        message = OnPushStatusMessage.from_json(message)
                        if message.isFullStatus() and self._on_push_full_status:
                            self._on_push_full_status(
                                self, message)
                        elif not message.isFullStatus() and self._on_push_status:
                            self._on_push_status(
                                self, message)
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

    def print(self, file: str, ams_mappings: Optional[list[int]] = None, http_server: Optional[str] = None, plate_number: int = 1):
        return self._publish(json.dumps(
            {
                "print": {
                    "sequence_id": "0",
                    "command": "project_file",
                    "param": f"Metadata/plate_{plate_number}.gcode",
                    "project_id": "0",  # Always 0 for local prints
                    "profile_id": "0",  # Always 0 for local prints
                    "task_id": "0",  # Always 0 for local prints
                    "subtask_id": "0",  # Always 0 for local prints
                    "url": f"file:///sdcard/{file}" if http_server is None else f"{http_server.replace("//", "///")}/{file}",

                    "timelapse": False,
                    "bed_type": "auto",  # Always "auto" for local prints
                    "bed_levelling": True,
                    "flow_cali": False,
                    "vibration_cali": False,
                    "layer_inspect": False,
                    "ams_mapping": ams_mappings if ams_mappings is not None else [],
                    "use_ams": ams_mappings is not None,
                    "job_type": 1
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

    def request_full_status(self):
        return self._publish(json.dumps(
            {
                "pushing": {
                    "sequence_id": "0",
                    "command": "pushall",
                    "version": 1,
                    "push_target": 1
                }
            }
        ))

import logging
from typing import Dict
from uuid import uuid4
from bambucli.bambu.gcodestate import GcodeState
from bambucli.bambu.mqttclient import MqttClient
from bambucli.bambu.printstages import MC_PRINT_STAGES
from bambucli.bambu.speedprofiles import SPEED_PROFILE, SpeedProfile
from bambucli.bambu.ssdpclient import SsdpClient
from bambucli.printerview import PrinterInfo, PrinterViewBackend, PrinterViewFrontend
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeRemainingColumn
from sshkeyboard import listen_keyboard, stop_listening

logger = logging.getLogger(__name__)


class PrintDialogue(PrinterViewFrontend):

    def __init__(self):
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn('[bold white]Printing... '),
            TextColumn('[bold blue]{task.fields[status]}'),
            BarColumn(),
            TaskProgressColumn(),
            transient=True
        )
        self._taskId = None

    def start(self):
        self._progress.start()
        self._taskId = self._progress.add_task(
            'Printing', total=100, status='Connecting...')

    def stop(self):
        self._progress.stop()

    def update(self, printer_info: Dict[str, PrinterInfo], selected_printer: str):
        print_status = printer_info[selected_printer].print_status
        if print_status.file is not None and print_status.file != '' and print_status.percent is not None and print_status.current_layer is not None and print_status.total_layers is not None:
            self._progress.update(
                self._taskId, status=print_status.state.name, completed=print_status.percent)


class PrintException(Exception):
    pass


def print_dialogue(printer, remote_path, ams_mapping, plate_number):

    dialogue = PrinterViewBackend([printer], frontend=PrintDialogue())

    queue = dialogue.queue

    dialogue.run()

    firstConnection = True
    printStarted = False
    printException = None

    def check_that_print_started(status):
        nonlocal printStarted
        if status.print_type is not None and status.print_type != 'idle':
            printStarted = True

    def check_status_for_termination_state(status):
        nonlocal printStarted, printException
        if status.print_error is not None:
            logger.info('Error encountered: ' + status.print_error.name)
            printException = PrintException(status.print_error.name)
            stop_listening()
        if status.print_type is not None and status.print_type == 'idle' and printStarted:
            logger.info('Print complete')
            stop_listening()

    def _on_connect(client, reason_code):
        nonlocal firstConnection
        if firstConnection:
            firstConnection = False

            def on_success():
                client.print(remote_path, ams_mappings=ams_mapping,
                             plate_number=plate_number)
                client.request_full_status()
            client.clean_print_error(onSuccess=on_success)
        else:
            client.request_full_status()

    def _on_push_full_status(client, status):
        queue.put((4, {
            'serial_number': client.serial_number,
            'type': 'status_update',
            'data': status
        }))
        if not printStarted:
            check_that_print_started(status)
        check_status_for_termination_state(status)

    def _on_push_status(client, status):
        queue.put((4, {
            'serial_number': client.serial_number,
            'type': 'status_update',
            'data': status
        }))
        if not printStarted:
            check_that_print_started(status)
        check_status_for_termination_state(status)

    def create_and_connect_mqtt_client(printer):
        bambuMqttClient = MqttClient.for_printer(
            printer, _on_connect, _on_push_status, _on_push_full_status)
        bambuMqttClient.connect()
        bambuMqttClient.loop_start()
        return bambuMqttClient

    client = create_and_connect_mqtt_client(printer)

    def on_press(key):
        match key:
            case 'c':
                logger.info('Cancelling print')
                client.stop_print()
            case 'q':
                logger.info('Quitting')
                stop_listening()
            case 'p':
                logger.info('Pausing')
                client.pause_print()
            case 'r':
                logger.info('Resuming')
                client.resume_print()
            case '1':
                logger.info('Setting speed to silent')
                client.set_print_speed(
                    SpeedProfile.SILENT)
            case '2':
                logger.info('Setting speed to standard')
                client.set_print_speed(
                    SpeedProfile.STANDARD)
            case '3':
                logger.info('Setting speed to sport')
                client.set_print_speed(
                    SpeedProfile.SPORT)
            case '4':
                logger.info('Setting speed to ludicrous')
                client.set_print_speed(
                    SpeedProfile.LUDICROUS)

    ssdp_close = SsdpClient().monitor_for_printers(lambda printer: queue.put((2, {
        'type': 'ssdp_printer',
        'data': printer
    })))

    listen_keyboard(
        on_press=on_press
    )

    client.loop_stop()
    client.disconnect()
    ssdp_close()
    dialogue.stop()
    if printException is not None:
        raise printException

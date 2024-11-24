import logging
from bambu.messages.onpushstatus import PrintErrorCode
from bambu.mqttclient import MqttClient
from bambu.printer import LocalPrinter
from config import get_printer
from sshkeyboard import listen_keyboard, stop_listening
import enlighten

logger = logging.getLogger(__name__)

STATUS_FORMAT = 'Status: {status} | File: {file} | Time Remaining: {minutes_remaining}mins ({percentage_done}%) | Layer: {current_layer}'


def print_file(args):

    printer = get_printer(args.printer)

    manager = enlighten.get_manager()
    manager.status_bar(
        status_format='Press "c" to cancel, "p" to pause, "r" to resume, "q" to quit',
        justify=enlighten.Justify.CENTER,
    )
    status_bar = manager.status_bar(
        status='Connecting',
        file='n/a',
        minutes_remaining='?',
        percentage_done='0',
        current_layer='0',
        status_format=STATUS_FORMAT,
        justify=enlighten.Justify.CENTER,
    )

    def on_connect(client, reason_code):
        status_bar.update(status='Connected')
        client.print(args.file)

    def on_push_status(client, status):
        stop = False

        if (status.gcode_file is not None):
            status_bar.update(file=status.gcode_file)
        if (status.mc_remaining_time is not None):
            status_bar.update(minutes_remaining=status.mc_remaining_time)
        if (status.mc_percent is not None):
            status_bar.update(percentage_done=status.mc_percent)
        if (status.layer_num is not None):
            status_bar.update(current_layer=status.layer_num)
        if (status.gcode_state is not None):
            status_bar.update(status=status.gcode_state)
            if (status.gcode_state == 'FINISH'):
                logger.info('Print finished')
                print('Done')
                stop = True

        if status.print_error is not None:
            match status.print_error:
                case PrintErrorCode.CANCELLED:
                    logger.info('Print cancelled')
                    print('Cancelled')
                case PrintErrorCode.FILE_NOT_FOUND:
                    logger.info('File not found')
                    print('File not found')
                case _:
                    logger.info('Print failed')
                    print('Failed')
            stop = True

        if stop:
            stop_listening()

    bambuMqttClient = MqttClient.for_printer(
        printer, on_connect, on_push_status)

    bambuMqttClient.connect()
    bambuMqttClient.loop_start()

    def on_press(key):
        match key:
            case 'c':
                logger.info('Cancelling print')
                bambuMqttClient.stop_print()
            case 'q':
                logger.info('Quitting')
                stop_listening()
            case 'p':
                logger.info('Pausing')
                bambuMqttClient.pause_print()
            case 'r':
                logger.info('Resuming')
                bambuMqttClient.resume_print()

    listen_keyboard(
        on_press=on_press
    )

    bambuMqttClient.loop_stop()
    bambuMqttClient.disconnect()

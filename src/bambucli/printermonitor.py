
import logging
from bambucli.bambu.messages.onpushstatus import PrintErrorCode
from bambucli.bambu.mqttclient import MqttClient
import enlighten
from sshkeyboard import listen_keyboard, stop_listening

STATUS_FORMAT = 'Status: {status} | File: {file} | Time Remaining: {minutes_remaining}mins ({percentage_done}%) | Layer: {current_layer}/{total_layers}'
logger = logging.getLogger(__name__)


def printer_monitor(printer, on_connect=lambda client, response_code: False, on_push_status=lambda client, status: False):
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
        current_layer='?',
        total_layers='?',
        status_format=STATUS_FORMAT,
        justify=enlighten.Justify.CENTER,
    )

    def update_status(status):
        if (status.gcode_file is not None):
            status_bar.update(file=status.gcode_file)
        if (status.mc_remaining_time is not None):
            status_bar.update(minutes_remaining=status.mc_remaining_time)
        if (status.mc_percent is not None):
            status_bar.update(percentage_done=status.mc_percent)
        if (status.layer_num is not None):
            status_bar.update(current_layer=status.layer_num)
        if (status.total_layer_num is not None):
            status_bar.update(total_layers=status.total_layer_num)
        if (status.gcode_state is not None):
            status_bar.update(status=status.gcode_state)

    def _on_connect(client, reason_code):
        status_bar.update(status='Connected')
        client.request_full_status()
        stop = on_connect(client, reason_code)
        if stop:
            stop_listening()

    def _on_push_full_status(client, status):
        update_status(status)

    def _on_push_status(client, status):
        stop = on_push_status(client, status)

        update_status(status)

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
        printer, _on_connect, _on_push_status, _on_push_full_status)

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
    # asyncio.run(file_server.shutdown()) if file_server else None

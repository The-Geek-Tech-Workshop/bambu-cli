from itertools import chain
import logging
from math import floor
from typing import Dict
from bambucli.bambu.mqttclient import MqttClient
from bambucli.bambu.printstages import MC_PRINT_STAGES
from bambucli.bambu.speedprofiles import SPEED_PROFILE, SpeedProfile
from bambucli.bambu.ssdpclient import SsdpClient
from bambucli.printerview import PrintStatus, PrinterInfo, PrinterViewBackend, PrinterViewFrontend
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from sshkeyboard import listen_keyboard, stop_listening

logger = logging.getLogger(__name__)


class PrinterDashboard(PrinterViewFrontend):

    def __init__(self):
        self._live = Live()

    def start(self):
        return self._live.start()

    def stop(self):
        return self._live.stop()

    def generate_dashboard(self, printer_info: Dict[str, PrinterInfo], selected_printer: str):

        printers = list(map(lambda i: i.printer, printer_info.values()))

        printer_table = Table(
            caption='< > = Select | c = Cancel | p = Pause | r = Resume | 1-4 = Set speed | q = Quit', min_width=70)
        printer_table.add_column()
        for printer in printers:
            printer_table.add_column(
                printer.name if printer.serial_number != selected_printer else f"[bold white][{printer.name}]", max_width=25)

        printer_table.add_row(
            '[bold]Model', *[printer.model.value for printer in printers])
        printer_table.add_row(
            '[bold]Serial', *[printer.serial_number for printer in printers])
        printer_table.add_row(
            '[bold]IP', *[info.ip_address if info.ip_address else '?' for info in printer_info.values()])
        printer_table.add_row(
            '[bold]Nozzle', *[(info.nozzle.diameter + "mm" if info.nozzle.diameter else "") + (' ' + info.nozzle.type if info.nozzle.type else '') for info in printer_info.values()])

        def format_firmware_version(module):
            if module is None:
                return '?'
            upgrade_available = module.new_version is not None and module.new_version != module.software_version
            return f"{module.software_version}{"*" if upgrade_available else ''}"
        printer_table.add_row(
            '[bold]Firmware', *[format_firmware_version(info.modules.get("ota", None)) for info in printer_info.values()], end_section=True)

        printer_table.add_row(
            '[bold]Chamber Temp', *[f"{'%.1f°C' % info.chamber.temperature if info.chamber.temperature else '?'}" for info in printer_info.values()])
        printer_table.add_row(
            '[bold]Print Bed Temp', *[f"{'%.1f°C' % info.print_bed.temperature if info.print_bed.temperature else '?'} {'/%.1f°C' % info.print_bed.target_temperature if info.print_bed.target_temperature else ''}" for info in printer_info.values()])
        printer_table.add_row(
            '[bold]Nozzle Temp', *[f"{'%.1f°C' % info.nozzle.temperature if info.nozzle.temperature else '?'} {'/%.1f°C' % info.nozzle.target_temperature if info.nozzle.target_temperature else ''}" for info in printer_info.values()])
        printer_table.add_row(
            '[bold]Wifi Signal', *[f"{info.wifi.signal_strength}" if info.wifi.signal_strength else '?' for info in printer_info.values()])
        printer_table.add_row(
            '[bold]Cooling Fan', *[f"{info.fan_speeds.cooling_fan}%" if info.fan_speeds.cooling_fan else '?' for info in printer_info.values()])
        printer_table.add_row(
            '[bold]Big Fan 1', *[f"{info.fan_speeds.big_fan1}%" if info.fan_speeds.big_fan1 else '?' for info in printer_info.values()])
        printer_table.add_row(
            '[bold]Big Fan 2', *[f"{info.fan_speeds.big_fan2}%" if info.fan_speeds.big_fan2 else '?' for info in printer_info.values()], end_section=True)

        def format_filament_colour(filament):
            if filament is None:
                return '-'
            if filament.colour_hex8:
                return f"[rgb({','.join(tuple(map(str, filament.colour_rgb())))})]{filament.material}"
            return filament.material

        printer_table.add_row(
            '[bold]External Spool', *[format_filament_colour(info.external_spool) if info.external_spool else '?' for info in printer_info.values()])

        all_filament_indexes = sorted(set(chain.from_iterable([info.ams_filaments.keys()
                                                               for info in printer_info.values()])))

        for index in all_filament_indexes:
            printer_table.add_row(
                f'[bold]AMS Tray {index + 1}', *[format_filament_colour(info.ams_filaments.get(index, None)) for info in printer_info.values()], end_section=index == all_filament_indexes[-1])

        active_print_types = set(['local', 'cloud'])
        printer_table.add_row(
            '[bold]Print State', *[info.print_status.state.value if info.print_status.state and info.print_status.type in active_print_types else 'n/a' for info in printer_info.values()])
        printer_table.add_row(
            '[bold]File', *[info.print_status.file if info.print_status.file and info.print_status.type in active_print_types else 'n/a' for info in printer_info.values()])
        printer_table.add_row(
            '[bold]Stage', *[MC_PRINT_STAGES.get(int(info.print_status.stage), f"Unknown: ({info.print_status.stage})") if info.print_status.stage is not None and info.print_status.type in active_print_types else 'n/a' for info in printer_info.values()])
        printer_table.add_row(
            '[bold]Speed', *[f"{SPEED_PROFILE.get(info.print_status.speed, f"Unknown: {info.print_status.speed}")}" if info.print_status.speed is not None and info.print_status.type in active_print_types else 'n/a' for info in printer_info.values()])

        def format_progress(print_status: PrintStatus):
            progress_bars_done = floor(
                print_status.percent / 10) if print_status.percent is not None else 0
            progress_bar = f"[red]{'-' * progress_bars_done}[/red][black]{
                '-' * (10 - progress_bars_done)}[/black] {print_status.percent}%" if print_status.percent is not None else 'n/a'
            layer_info = f"({print_status.current_layer}/{
                print_status.total_layers})" if print_status.current_layer is not None and print_status.total_layers is not None else 'n/a'
            return f"{progress_bar} {layer_info}"
        printer_table.add_row(
            '[bold]Progress', *[format_progress(info.print_status) if info.print_status.type in active_print_types else 'n/a' for info in printer_info.values()])

        return Layout(Align.center(printer_table))

    def update(self, printer_info: Dict[str, PrinterInfo], selected_printer: str):
        self._live.update(self.generate_dashboard(
            printer_info, selected_printer))


def dashboard(*printers):

    dashboard = PrinterViewBackend(printers, frontend=PrinterDashboard())

    queue = dashboard.queue

    dashboard.run()

    def _on_connect(client, reason_code):
        client.request_full_status()
        client.request_version_info()

    def _on_push_full_status(client, status):
        queue.put((4, {
            'serial_number': client.serial_number,
            'type': 'status_update',
            'data': status
        }))

    def _on_push_status(client, status):
        queue.put((4, {
            'serial_number': client.serial_number,
            'type': 'status_update',
            'data': status
        }))

    def _on_get_version(client, version):
        queue.put((4, {
            'serial_number': client.serial_number,
            'type': 'version_update',
            'data': version
        }))

    def create_and_connect_mqtt_client(printer):
        bambuMqttClient = MqttClient.for_printer(
            printer, _on_connect, _on_push_status, _on_push_full_status, _on_get_version)
        bambuMqttClient.connect()
        bambuMqttClient.loop_start()
        return bambuMqttClient

    clients = list(map(create_and_connect_mqtt_client, printers))

    selected_printer = 0

    def on_press(key):
        nonlocal selected_printer
        match key:
            case 'c':
                logger.info('Cancelling print')
                clients[selected_printer].stop_print()
            case 'q':
                logger.info('Quitting')
                stop_listening()
            case 'p':
                logger.info('Pausing')
                clients[selected_printer].pause_print()
            case 'r':
                logger.info('Resuming')
                clients[selected_printer].resume_print()
            case '1':
                logger.info('Setting speed to silent')
                clients[selected_printer].set_print_speed(
                    SpeedProfile.SILENT)
            case '2':
                logger.info('Setting speed to standard')
                clients[selected_printer].set_print_speed(
                    SpeedProfile.STANDARD)
            case '3':
                logger.info('Setting speed to sport')
                clients[selected_printer].set_print_speed(
                    SpeedProfile.SPORT)
            case '4':
                logger.info('Setting speed to ludicrous')
                clients[selected_printer].set_print_speed(
                    SpeedProfile.LUDICROUS)
            case 'right':
                selected_printer = (selected_printer + 1) % len(printers)
                queue.put((3, {'type': 'select_printer',
                               'data': selected_printer}))
            case 'left':
                selected_printer = (selected_printer - 1) % len(printers)
                queue.put((3, {'type': 'select_printer',
                               'data': selected_printer}))

    ssdp_close = SsdpClient().monitor_for_printers(lambda printer: queue.put((2, {
        'type': 'ssdp_printer',
        'data': printer
    })))

    listen_keyboard(
        on_press=on_press
    )

    for client in clients:
        client.loop_stop()
        client.disconnect()
    ssdp_close()
    dashboard.stop()


from dataclasses import dataclass, field
from itertools import chain
import logging
from math import floor
from queue import PriorityQueue
import threading
from typing import Dict, List, Optional
from bambucli.bambu.mqttclient import MqttClient
from bambucli.bambu.printer import Printer
from bambucli.bambu.printstages import MC_PRINT_STAGES
from bambucli.bambu.speedprofiles import SPEED_PROFILE, SpeedProfile
from bambucli.bambu.ssdpclient import SsdpClient
from rich.align import Align
from rich.layout import Layout
from rich.live import Live
from rich.table import Table
from sshkeyboard import listen_keyboard, stop_listening

logger = logging.getLogger(__name__)


@dataclass
class Chamber():
    temperature: float = field(default_factory=lambda: None)


@dataclass
class PrintBed():
    temperature: float = field(default_factory=lambda: None)
    target_temperature: float = field(default_factory=lambda: None)


@dataclass
class Nozzle():
    diameter: str = field(default_factory=lambda: None)
    type: str = field(default_factory=lambda: None)
    temperature: float = field(default_factory=lambda: None)
    target_temperature: float = field(default_factory=lambda: None)


@dataclass
class Wifi():
    signal_strength: str = field(default_factory=lambda: None)


@dataclass
class PrintStatus():
    file: str = field(default_factory=lambda: None)
    state: str = field(default_factory=lambda: None)
    type: str = field(default_factory=lambda: None)
    remaining_time: int = field(default_factory=lambda: None)
    percent: int = field(default_factory=lambda: None)
    current_layer: int = field(default_factory=lambda: None)
    total_layers: int = field(default_factory=lambda: None)
    state: str = field(default_factory=lambda: None)
    stage: int = field(default_factory=lambda: None)
    speed: int = field(default_factory=lambda: None)


@dataclass
class FanSpeeds():
    cooling_fan: int = field(default_factory=lambda: None)
    big_fan1: int = field(default_factory=lambda: None)
    big_fan2: int = field(default_factory=lambda: None)


@dataclass
class Filament:
    material: str
    colour_hex8: str

    def colour_rgb(self):
        return tuple(int(self.colour_hex8[i:i+2], 16) for i in (0, 2, 4))


@dataclass
class ModuleVersion:
    name: str
    project_name: str
    software_version: str
    new_version: str
    hardware_version: str
    serial_number: str
    loader_version: str


@dataclass
class PrinterInfo():
    printer: Printer
    ip_address: str = field(default_factory=lambda: None)
    chamber: Chamber = field(default_factory=lambda: Chamber())
    print_bed: PrintBed = field(default_factory=lambda: PrintBed())
    nozzle: Nozzle = field(default_factory=lambda: Nozzle())
    fan_speeds: FanSpeeds = field(default_factory=lambda: FanSpeeds())
    wifi: Wifi = field(default_factory=lambda: Wifi())
    print_status: PrintStatus = field(default_factory=lambda: PrintStatus())
    external_spool: Optional[Filament] = field(default_factory=lambda: None)
    ams_filaments: Dict[int, Filament] = field(default_factory=dict)
    # network_addresses: List[IPv4Network] = field(default_factory=list)
    lights_report: Dict[str, str] = field(default_factory=dict)
    modules: Dict[str, ModuleVersion] = field(default_factory=dict)


class PrinterDashboard():
    def __init__(self, *printers, queue: PriorityQueue, live: Live):
        self.printer_info = {}
        self.printers = printers
        for printer in printers:
            self.printer_info[printer.serial_number] = PrinterInfo(
                printer=printer)
        self.selected_printer = 0

        self.queue = queue
        self.live = live

    def _run(self):
        while True:
            (priority, message) = self.queue.get()
            match message['type']:
                case 'status_update':
                    self.update_status(
                        message['data'], message['serial_number'])
                case 'version_update':
                    self.update_info(message['data'], message['serial_number'])
                case 'select_printer':
                    self.select_printer(message['data'])
                case 'ssdp_printer':
                    self.ssdp_printer(message['data'])
                case 'stop':
                    break
            self.update_display()

    def run(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        if self._thread:
            self.queue.put((1, {'type': 'stop'}))
            self._thread.join()

    def ssdp_printer(self, printer):
        info = self.printer_info.get(printer.serial_number, None)
        if info is not None:
            info.ip_address = printer.ip_address
            self.update_display()

    def select_printer(self, index):
        self.selected_printer = index

    def update_info(self, info, serial_number):
        for module in info.modules:
            self.printer_info[serial_number].modules[module.name] = ModuleVersion(
                name=module.name,
                project_name=module.project_name,
                software_version=module.sw_ver,
                new_version=module.new_ver,
                hardware_version=module.hw_ver,
                serial_number=module.sn,
                loader_version=module.loader_ver
            )

    def update_status(self, status, serial_number):
        if status.chamber_temper is not None:
            self.printer_info[serial_number].chamber.temperature = status.chamber_temper
        if status.bed_temper is not None:
            self.printer_info[serial_number].print_bed.temperature = status.bed_temper
        if status.bed_target_temper is not None:
            self.printer_info[serial_number].print_bed.target_temperature = status.bed_target_temper
        if status.nozzle_diameter is not None:
            self.printer_info[serial_number].nozzle.diameter = status.nozzle_diameter
        if status.nozzle_type is not None:
            self.printer_info[serial_number].nozzle.type = status.nozzle_type
        if status.nozzle_temper is not None:
            self.printer_info[serial_number].nozzle.temperature = status.nozzle_temper
        if status.nozzle_target_temper is not None:
            self.printer_info[serial_number].nozzle.target_temperature = status.nozzle_target_temper
        if status.wifi_signal is not None:
            self.printer_info[serial_number].wifi.signal_strength = status.wifi_signal
        if status.cooling_fan_speed is not None:
            self.printer_info[serial_number].fan_speeds.cooling_fan = status.cooling_fan_speed
        if status.big_fan1_speed is not None:
            self.printer_info[serial_number].fan_speeds.big_fan1 = status.big_fan1_speed
        if status.big_fan2_speed is not None:
            self.printer_info[serial_number].fan_speeds.big_fan2 = status.big_fan2_speed
        if status.lights_report is not None:
            for light in status.lights_report:
                self.printer_info[serial_number].lights_report[light.node] = light.mode

        if status.gcode_state is not None:
            self.printer_info[serial_number].print_status.state = status.gcode_state
        if status.print_type is not None:
            self.printer_info[serial_number].print_status.type = status.print_type
        if status.gcode_file is not None:
            self.printer_info[serial_number].print_status.file = status.gcode_file
        if status.mc_remaining_time is not None:
            self.printer_info[serial_number].print_status.remaining_time = status.mc_remaining_time
        if status.mc_percent is not None:
            self.printer_info[serial_number].print_status.percent = status.mc_percent
        if status.layer_num is not None:
            self.printer_info[serial_number].print_status.current_layer = status.layer_num
        if status.total_layer_num is not None:
            self.printer_info[serial_number].print_status.total_layers = status.total_layer_num
        if status.stg_cur is not None:
            self.printer_info[serial_number].print_status.stage = status.stg_cur
        if status.spd_lvl is not None:
            self.printer_info[serial_number].print_status.speed = status.spd_lvl

        if status.vt_tray:
            self.printer_info[serial_number].external_spool = Filament(
                material=status.vt_tray.tray_type, colour_hex8=status.vt_tray.tray_color)

        if status.ams:
            for ams_module in status.ams.ams:
                for tray in ams_module.trays:
                    self.printer_info[serial_number].ams_filaments[int(tray.id)] = Filament(
                        material=tray.tray_type, colour_hex8=tray.tray_color)
        # if status.net:
        #     self.printer_info[serial_number].network_addresses = status.net.info

    def generate_dashboard(self):

        printer_table = Table(
            caption='< > = Select | c = Cancel | p = Pause | r = Resume | 1-4 = Set speed | q = Quit', min_width=70)
        printer_table.add_column()
        for printer in self.printers:
            printer_table.add_column(
                printer.name if printer != self.printers[self.selected_printer] else f"[bold white][{printer.name}]", max_width=25)

        printer_table.add_row(
            '[bold]Model', *[printer.model.value for printer in self.printers])
        printer_table.add_row(
            '[bold]Serial', *[printer.serial_number for printer in self.printers])
        printer_table.add_row(
            '[bold]IP', *[info.ip_address if info.ip_address else '?' for info in self.printer_info.values()])
        printer_table.add_row(
            '[bold]Nozzle', *[(info.nozzle.diameter + "mm" if info.nozzle.diameter else "") + (' ' + info.nozzle.type if info.nozzle.type else '') for info in self.printer_info.values()])

        def format_firmware_version(module):
            if module is None:
                return '?'
            upgrade_available = module.new_version is not None and module.new_version != module.software_version
            return f"{module.software_version}{"*" if upgrade_available else ''}"
        printer_table.add_row(
            '[bold]Firmware', *[format_firmware_version(info.modules.get("ota", None)) for info in self.printer_info.values()], end_section=True)

        printer_table.add_row(
            '[bold]Chamber Temp', *[f"{'%.1f°C' % info.chamber.temperature if info.chamber.temperature else '?'}" for info in self.printer_info.values()])
        printer_table.add_row(
            '[bold]Print Bed Temp', *[f"{'%.1f°C' % info.print_bed.temperature if info.print_bed.temperature else '?'} {'/%.1f°C' % info.print_bed.target_temperature if info.print_bed.target_temperature else ''}" for info in self.printer_info.values()])
        printer_table.add_row(
            '[bold]Nozzle Temp', *[f"{'%.1f°C' % info.nozzle.temperature if info.nozzle.temperature else '?'} {'/%.1f°C' % info.nozzle.target_temperature if info.nozzle.target_temperature else ''}" for info in self.printer_info.values()])
        printer_table.add_row(
            '[bold]Wifi Signal', *[f"{info.wifi.signal_strength}" if info.wifi.signal_strength else '?' for info in self.printer_info.values()])
        printer_table.add_row(
            '[bold]Cooling Fan', *[f"{info.fan_speeds.cooling_fan}%" if info.fan_speeds.cooling_fan else '?' for info in self.printer_info.values()])
        printer_table.add_row(
            '[bold]Big Fan 1', *[f"{info.fan_speeds.big_fan1}%" if info.fan_speeds.big_fan1 else '?' for info in self.printer_info.values()])
        printer_table.add_row(
            '[bold]Big Fan 2', *[f"{info.fan_speeds.big_fan2}%" if info.fan_speeds.big_fan2 else '?' for info in self.printer_info.values()], end_section=True)

        def format_filament_colour(filament):
            if filament is None:
                return '-'
            if filament.colour_hex8:
                return f"[rgb({','.join(tuple(map(str, filament.colour_rgb())))})]{filament.material}"
            return filament.material

        printer_table.add_row(
            '[bold]External Spool', *[format_filament_colour(info.external_spool) if info.external_spool else '?' for info in self.printer_info.values()])

        all_filament_indexes = sorted(set(chain.from_iterable([info.ams_filaments.keys()
                                                               for info in self.printer_info.values()])))

        for index in all_filament_indexes:
            printer_table.add_row(
                f'[bold]AMS Tray {index + 1}', *[format_filament_colour(info.ams_filaments.get(index, None)) for info in self.printer_info.values()], end_section=index == all_filament_indexes[-1])

        active_print_types = set(['local', 'cloud'])
        printer_table.add_row(
            '[bold]Print State', *[info.print_status.state if info.print_status.state and info.print_status.type in active_print_types else 'n/a' for info in self.printer_info.values()])
        printer_table.add_row(
            '[bold]File', *[info.print_status.file if info.print_status.file and info.print_status.type in active_print_types else 'n/a' for info in self.printer_info.values()])
        printer_table.add_row(
            '[bold]Stage', *[MC_PRINT_STAGES.get(int(info.print_status.stage), f"Unknown: ({info.print_status.stage})") if info.print_status.stage is not None and info.print_status.type in active_print_types else 'n/a' for info in self.printer_info.values()])
        printer_table.add_row(
            '[bold]Speed', *[f"{SPEED_PROFILE.get(info.print_status.speed, f"Unknown: {info.print_status.speed}")}" if info.print_status.speed is not None and info.print_status.type in active_print_types else 'n/a' for info in self.printer_info.values()])

        def format_progress(print_status: PrintStatus):
            progress_bars_done = floor(
                print_status.percent / 10) if print_status.percent is not None else 0
            progress_bar = f"[red]{'-' * progress_bars_done}[/red][black]{
                '-' * (10 - progress_bars_done)}[/black] {print_status.percent}%" if print_status.percent is not None else 'n/a'
            layer_info = f"({print_status.current_layer}/{
                print_status.total_layers})" if print_status.current_layer is not None and print_status.total_layers is not None else 'n/a'
            return f"{progress_bar} {layer_info}"
        printer_table.add_row(
            '[bold]Progress', *[format_progress(info.print_status) if info.print_status.type in active_print_types else 'n/a' for info in self.printer_info.values()])

        return Layout(Align.center(printer_table))

    def update_display(self):
        self.live.update(self.generate_dashboard())


def dashboard(*printers):

    with Live() as live:

        queue = PriorityQueue()

        dashboard = PrinterDashboard(*printers, live=live, queue=queue)
        dashboard.update_display()
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


from abc import ABC
from dataclasses import dataclass, field
import logging
from math import floor
from queue import PriorityQueue
import threading
from typing import Dict, List, Optional
from bambucli.bambu.gcodestate import GcodeState
from bambucli.bambu.printer import Printer

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
    state: GcodeState = field(default_factory=lambda: None)
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
    lights_report: Dict[str, str] = field(default_factory=dict)
    modules: Dict[str, ModuleVersion] = field(default_factory=dict)


class PrinterViewFrontend(ABC):
    def update(self, printer_info: Dict[str, PrinterInfo], selected_printer: int):
        raise NotImplementedError()

    def start(self):
        raise NotImplementedError()

    def stop(self):
        raise NotImplementedError()


class PrinterViewBackend():
    def __init__(self, printers: List[Printer], frontend: PrinterViewFrontend):
        self.printer_info = {}
        self.printers = printers
        for printer in printers:
            self.printer_info[printer.serial_number] = PrinterInfo(
                printer=printer)
        self.selected_printer = 0
        self.queue = PriorityQueue()
        self._frontend = frontend
        self._thread = None

    def update_frontend(self):
        self._frontend.update(
            self.printer_info, self.printers[self.selected_printer].serial_number)

    def _run(self):
        self._frontend.start()
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
            self.update_frontend()

    def run(self):
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        if self._thread:
            self.queue.put((1, {'type': 'stop'}))
            self._thread.join()
        self._frontend.stop()

    def ssdp_printer(self, printer):
        info = self.printer_info.get(printer.serial_number, None)
        if info is not None:
            info.ip_address = printer.ip_address

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

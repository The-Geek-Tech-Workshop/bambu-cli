from dataclasses import dataclass
from enum import Enum


class PrinterModel(Enum):
    P1 = 'P1'
    A1 = 'A1'
    UNKNOWN = 'Unknown'


class Printer():
    pass


@dataclass
class LocalPrinter(Printer):
    ip_address: str
    serial_number: str
    access_code: str
    model: PrinterModel
    name: str = None

    def id(self):
        return self.name if self.name is not None else self.serial_number

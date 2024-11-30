from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PrinterModel(Enum):
    X1 = 'X1'
    X1C = 'X1C'
    P1S = 'P1S'
    P1P = 'P1P'
    A1 = 'A1'
    A1MINI = 'A1Mini'
    UNKNOWN = 'Unknown'

    @staticmethod
    def from_model_code(model_code: str):
        return {
            'BL-P002': PrinterModel.X1,
            'BL-P001': PrinterModel.X1C,
            'C12': PrinterModel.P1S,
            'C11': PrinterModel.P1P,
            'N1': PrinterModel.A1MINI,
            'N2S': PrinterModel.A1
        }.get(model_code, PrinterModel.UNKNOWN)


@dataclass
class Printer():
    serial_number: str
    name: Optional[str]
    access_code: str
    account_email: Optional[str]
    ip_address: Optional[str]
    model: PrinterModel

    def id(self):
        return self.name if self.name is not None else self.serial_number

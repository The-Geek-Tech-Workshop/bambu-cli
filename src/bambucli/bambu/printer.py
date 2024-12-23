from dataclasses import dataclass
from enum import Enum
from typing import Optional


class PrinterMake(Enum):
    BAMBU = 'Bambu'
    ULTIMAKER = 'Ultimaker'
    UNKNOWN = 'Unknown'

    @staticmethod
    def from_make(make: str):
        return {
            'Bambu': PrinterMake.BAMBU,
            'Ultimaker': PrinterMake.ULTIMAKER
        }.get(make, PrinterMake.UNKNOWN)


class PrinterModel(Enum):
    # Bambu
    X1 = 'X1'
    X1C = 'X1C'
    P1S = 'P1S'
    P1P = 'P1P'
    A1 = 'A1'
    A1MINI = 'A1Mini'

    # Ultimaker
    ULT3 = 'Ult3'
    ULT3_EXT = 'Ult3_Ext'
    UNKNOWN = 'Unknown'

    @staticmethod
    def from_bambu_model_code(model_code: str):
        return {
            'BL-P002': PrinterModel.X1,
            'BL-P001': PrinterModel.X1C,
            'C12': PrinterModel.P1S,
            'C11': PrinterModel.P1P,
            'N1': PrinterModel.A1MINI,
            'N2S': PrinterModel.A1
        }.get(model_code, PrinterModel.UNKNOWN)

    @staticmethod
    def from_ultimaker_hardware_type_id(variant: int):
        return {
            9066: PrinterModel.ULT3,
            9511: PrinterModel.ULT3_EXT
        }.get(variant, PrinterModel.UNKNOWN)

    def make(self):
        if self in [PrinterModel.X1, PrinterModel.X1C, PrinterModel.P1S, PrinterModel.P1P, PrinterModel.A1, PrinterModel.A1MINI]:
            return PrinterMake.BAMBU
        elif self in [PrinterModel.ULT3]:
            return PrinterMake.ULTIMAKER
        else:
            return PrinterMake.UNKNOWN


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


from dataclasses import dataclass

from bambucli.bambu.printer import PrinterModel
from bambucli.basetypes import Printer


@dataclass
class LoginDetails:
    id: str
    key: str


@dataclass
class UltimakerPrinter(Printer):
    name: str
    ip_address: str
    login_details: LoginDetails
    model: PrinterModel

from dataclasses import dataclass


class Printer():
    pass


@dataclass
class LocalPrinter(Printer):
    ip_address: str
    serial_number: str
    access_code: str
    name: str = None

    def id(self):
        return self.name if self.name is not None else self.serial_number

from abc import ABC

from bambucli.bambu.printer import PrinterModel


class Printer(ABC):

    def id(self) -> str:
        pass

    def model(self) -> PrinterModel:
        pass

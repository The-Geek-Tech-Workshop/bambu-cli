

import dataclasses
from bambucli.bambu.ssdpclient import SsdpClient


class PrinterNotFoundOnNetworkException(Exception):
    def __init__(self):
        super().__init__("Printer not found on network")


def ensure_printer_ip_address(printer):
    """Ensure that the printer has an IP address

    Args:
        printer: Printer object

    Returns:
        printer: Printer object with ip_address attribute
    """
    def lookup_ip_address():
        ssdpClient = SsdpClient()
        local_printer = ssdpClient.get_printer(printer.serial_number)
        if not local_printer:
            return None
        return local_printer.ip_address

    if printer.ip_address:
        return printer

    ip_address = lookup_ip_address()
    if ip_address is None:
        raise PrinterNotFoundOnNetworkException()

    return dataclasses.replace(printer, ip_address=ip_address)

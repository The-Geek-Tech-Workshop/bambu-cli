import asyncio
import socket

from bambucli.bambu.printer import PrinterModel
from ssdp import aio
from dataclasses import dataclass

BAMBU_SSDP_PORT = 2021


@dataclass
class DiscoveredPrinter():
    serial_number: str
    name: str
    ip_address: str
    model: PrinterModel


class SsdpClient():

    class SsdpClientProtocol(aio.SimpleServiceDiscoveryProtocol):
        def __init__(self, loop):
            super().__init__()
            self.stop = loop.stop
            self.printers = {}

        def response_received(self, response, addr):
            pass

        def request_received(self, request, addr):
            data = dict(request.headers)
            if (data.get('NT') == 'urn:bambulab-com:device:3dprinter:1'):
                try:
                    printer = DiscoveredPrinter(
                        serial_number=data.get('USN'),
                        name=data.get('DevName.bambu.com'),
                        ip_address=data.get('Location'),
                        model=PrinterModel.from_model_code(
                            data.get('DevModel.bambu.com')),
                    )
                    self.printers[printer.serial_number] = printer
                except Exception as e:
                    print(e)

    def discoverPrinters(self, timeout=20):
        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', BAMBU_SSDP_PORT))
        connect = loop.create_datagram_endpoint(
            lambda: self.SsdpClientProtocol(loop), sock=sock)
        transport, protocol = loop.run_until_complete(connect)

        loop.run_until_complete(asyncio.sleep(timeout))

        transport.close()
        loop.close()

        return list(protocol.printers.values())

import asyncio
from queue import PriorityQueue
import socket
import threading
from typing import Callable, List, Optional

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
        def __init__(self, loop, serial_number=None, callback=None):
            super().__init__()
            self.stop = loop.stop
            self._serial_number = serial_number
            self._callback = callback
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
                    if self._callback:
                        self._callback(printer)
                    if printer.serial_number == self._serial_number or self._serial_number is None:
                        self.printers[printer.serial_number] = printer
                        if self._serial_number:
                            self.stop()
                except Exception as e:
                    print(e)

    def _listen_for_printers(self, timeout: Optional[int] = None, serial_number: Optional[str] = None, callback: Optional[Callable] = None) -> List[DiscoveredPrinter]:
        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', BAMBU_SSDP_PORT))
        connect = loop.create_datagram_endpoint(
            lambda: self.SsdpClientProtocol(loop, serial_number=serial_number, callback=callback), sock=sock)
        transport, protocol = loop.run_until_complete(connect)

        if timeout:
            try:
                loop.run_until_complete(asyncio.sleep(timeout))

            except Exception:
                # Ignore the exception, we're just using this to break out of the loop
                pass
            finally:
                transport.close()
                sock.close()
        else:
            thread = threading.Thread(target=loop.run_forever, daemon=True)
            thread.start()
            protocol.close = lambda: (
                loop.stop(), transport.close(), sock.close()
            )

        return protocol

    def monitor_for_printers(self, callback: Callable[[DiscoveredPrinter], None]) -> Callable:
        return self._listen_for_printers(
            serial_number=None, callback=callback).close

    def discover_printers(self, timeout: int = 20) -> List[DiscoveredPrinter]:
        printers = list(self._listen_for_printers(
            timeout=timeout).printers.values())
        return printers

    def get_printer(self, serial_number: str, timeout: int = 20) -> Optional[DiscoveredPrinter]:
        printers = list(self._listen_for_printers(
            timeout, serial_number).printers.values())
        if len(printers) == 0:
            return None
        return printers[0]

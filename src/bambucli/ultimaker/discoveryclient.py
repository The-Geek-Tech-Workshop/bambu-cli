
import asyncio
from dataclasses import dataclass
from typing import List

from zeroconf import Zeroconf, ServiceListener, ServiceBrowser


@dataclass
class DiscoveredUltimakerPrinter:
    pass


class MDNSClient():

    class UltimakerPrinterListener(ServiceListener):
        def __init__(self):
            self._printers = []

        def remove_service(self, zeroconf, type, name):
            print("Service %s removed" % (name,))

        def add_service(self, zeroconf, type, name):
            print("Service %s added" % (name,))
            info = zeroconf.get_service_info(type, name)
            if info:
                print("Service %s added, service info: %s" % (name, info))

    def discover_printers(self, timeout: int = 20) -> List[DiscoveredUltimakerPrinter]:
        zeroconf = Zeroconf()
        listener = self.UltimakerPrinterListener()
        loop = asyncio.get_event_loop()
        print("Browsing services, press Ctrl-C to exit...")
        ServiceBrowser(
            zeroconf, "_services._dns-sd._udp.local.", listener)

        try:
            loop.run_until_complete(asyncio.sleep(timeout))
        except Exception:
            # Ignore the exception, we're just using this to break out of the loop
            pass
        finally:
            print("Exiting")
            zeroconf.close()

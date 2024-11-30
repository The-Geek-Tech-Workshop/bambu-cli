
from bambucli.config import get_cloud_account, get_printer
from bambucli.printermonitor import printer_monitor


def monitor(args):
    printer = get_printer(args.printer)

    if printer is None:
        print(f"Printer '{args.printer}' not found")
        return

    printer_monitor(printer)

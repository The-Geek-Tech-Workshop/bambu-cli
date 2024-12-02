
from bambucli.config import get_cloud_account, get_printer
from bambucli.printermonitor import printer_monitor
from bambucli.spinner import Spinner


def monitor(args):

    spinner = Spinner()
    spinner.task_in_progress("Fetching printer details")
    try:
        printer = get_printer(args.printer)
        spinner.task_complete()
    except Exception as e:
        spinner.task_failed(e)
        return

    if printer is None:
        spinner.task_failed(f"Printer '{args.printer}' not found")
        return

    printer_monitor(printer)

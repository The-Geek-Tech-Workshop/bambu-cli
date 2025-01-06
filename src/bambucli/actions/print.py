from pathlib import Path
from bambucli.actions.ensureip import ensure_printer_ip_address
from bambucli.bambu.ftpclient import CACHE_DIRECTORY, FtpClient
from bambucli.config import get_printer
from bambucli.printdialogue import print_dialogue
from bambucli.spinner import Spinner


def print_file(args):

    spinner = Spinner()
    spinner.task_in_progress("Checking file")
    file_path = Path(args.file)
    if file_path.exists() is False:
        spinner.task_failed(f"File '{args.file}' not found")
        return

    spinner.task_in_progress("Fetching printer details")
    printer = None
    try:
        printer = get_printer(args.printer)
    except Exception as e:
        spinner.task_failed(e)
        return
    if printer is None:
        spinner.task_failed(f"Printer '{args.printer}' not found")
        return
    spinner.task_complete()

    ams_mapping = list(map(lambda filament: -1 if filament ==
                           'x' else filament, args.ams if args.ams else []))

    if printer.ip_address is None:
        spinner.task_in_progress("Checking for printer ip address")
        try:
            printer = ensure_printer_ip_address(printer)
            spinner.task_complete()
        except Exception as e:
            spinner.task_failed(e)
            return

    spinner.task_in_progress("Uploading file to printer")

    remote_path = f"{CACHE_DIRECTORY}{file_path.name}"

    try:
        ftps = FtpClient(printer.ip_address, printer.access_code)
        ftps.connect()
        ftps.upload_file(local_path=file_path, remote_path=remote_path)
    except Exception as e:
        spinner.task_failed(e)
        return
    try:
        ftps.quit()
    except:
        pass
    spinner.task_complete()

    try:
        print_dialogue(printer, remote_path, ams_mapping, args.plate)
        spinner.task_in_progress("Printing")
        spinner.task_complete()
    except Exception as e:
        spinner.task_in_progress("Printing")
        spinner.task_failed(e)
        return

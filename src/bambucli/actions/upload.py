from pathlib import Path
from bambucli.actions.ensureip import ensure_printer_ip_address
from bambucli.bambu.ftpclient import CACHE_DIRECTORY, FtpClient
from bambucli.bambu.ssdpclient import SsdpClient
from bambucli.config import get_printer
from bambucli.spinner import Spinner

BAMBU_FTP_PORT = 990
BAMBU_FTP_USER = 'bblp'


def upload_file(args) -> bool:
    """
    Upload file to Bambu printer via FTPS.

    Args:
        args: Namespace containing:
            printer: Printer identifier
            file: Path of local file to upload
    """
    spinner = Spinner()
    file = Path(args.file)
    spinner.task_in_progress("Checking file")
    if not file.exists():
        spinner.task_failed(f"File {args.file} not found")
        return
    spinner.task_complete()

    spinner.task_in_progress("Fetching printer details")
    printer = get_printer(args.printer)
    if not printer:
        spinner.task_failed(f"Printer {args.printer} not found in config")
        return
    spinner.task_complete()

    if printer.ip_address is None:
        spinner.task_in_progress("Checking for printer ip address")
        try:
            printer = ensure_printer_ip_address(printer)
            spinner.task_complete()
        except Exception as e:
            spinner.task_failed(e)
            return

    ftps = FtpClient(printer.ip_address, printer.access_code)

    spinner.task_in_progress(f"Connecting to printer {printer.id()}")
    try:
        ftps.connect()
    except Exception as e:
        spinner.task_failed(e)
        return
    spinner.task_complete()

    spinner.task_in_progress(f"Uploading file {args.file}")
    try:
        ftps.upload_file(file, f"{CACHE_DIRECTORY}{file.name}")
    except Exception as e:
        spinner.task_failed(e)
        return
    spinner.task_complete()

    try:
        ftps.quit()
    except:
        pass

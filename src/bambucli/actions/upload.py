from bambucli.bambu.ftpclient import FtpClient
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
            file: Local file path to upload
    """
    printer = get_printer(args.printer)
    if not printer:
        print(f"Printer {args.printer} not found in config")
        return

    ftps = FtpClient(printer.ip_address, printer.access_code)

    spinner = Spinner()
    spinner.task_in_progress(f"Connecting to printer {
                             printer.id()}", lambda: ftps.connect())
    spinner.task_in_progress(
        f"Uploading file {args.file}", lambda: ftps.upload_file(args.file))

    try:
        ftps.quit()
    except:
        pass

    return

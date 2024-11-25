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
        return False

    ftps = FtpClient(printer.ip_address, printer.access_code)

    with Spinner() as spinner:

        spinner.task_in_progress(f"Connecting to printer {printer.id()}")
        ftps.connect()
        spinner.task_complete()
        spinner.task_in_progress(f"Uploading file {args.file}")
        success = ftps.upload_file(args.file)

        try:
            ftps.quit()
        except:
            pass

        if success:
            spinner.task_complete()
        else:
            spinner.task_failed()

        return success

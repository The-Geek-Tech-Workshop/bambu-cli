from bambu.ftpclient import FtpClient
from config import get_printer

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

    print(f'Uploading {args.file} to printer {printer.id()}')

    ftps = FtpClient(printer.ip_address, printer.access_code)
    ftps.connect()
    success = ftps.upload_file(args.file)

    try:
        ftps.quit()
    except:
        pass

    if success:
        print("Upload successful")
    else:
        print("Upload failed")

    return success

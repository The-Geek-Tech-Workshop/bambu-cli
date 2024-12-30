

from bambucli.bambu.ftpclient import FtpClient
from bambucli.config import get_printer


def list_sd_files(args):
    """
    List files in the SD card
    """

    printer = get_printer(args.printer)
    ftp_client = FtpClient(args.ip, printer.access_code)
    files = ftp_client.list_files()
    print("Files in SD card:")
    for file in files:
        print(file)

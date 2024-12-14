from pathlib import Path
from bambucli.actions.ensureip import ensure_printer_ip_address
from bambucli.bambu.ftpclient import CACHE_DIRECTORY, FtpClient
from bambucli.config import get_printer
from bambucli.printermonitor import printer_monitor
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

    # spinner.task_in_progress("Checking for ngrok token")
    # ngrok_auth_token = None
    # try:
    #     ngrok_auth_token = get_ngrok_auth_token()
    # except Exception as e:
    #     spinner.task_failed(e)
    #     return
    # spinner.task_complete()

    # file_server, http_server = _start_tunneled_file_server(
    #     ngrok_auth_token, spinner)

    def on_connect(client, reason_code):
        client.print(remote_path, ams_mappings=ams_mapping)

    printer_monitor(printer, on_connect=on_connect)

    # if file_server:
    #     spinner.task_in_progress(
    #         "Shutting down file server", lambda: asyncio.run(file_server.shutdown()))


# def _start_tunneled_file_server(token, spinner):
#     if token:
#         spinner.task_in_progress("Starting tunneled file server")
#         try:
#             file_server = FileServer()
#             http_server = file_server.serve(token)
#             spinner.task_complete()
#             return file_server, http_server
#         except Exception as e:
#             spinner.task_failed(e)
#             return None, None
#     else:
#         return None, None

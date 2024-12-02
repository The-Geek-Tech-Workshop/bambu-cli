import asyncio
from bambucli.config import get_ngrok_auth_token, get_printer
from bambucli.fileserver import FileServer
from bambucli.printermonitor import printer_monitor
from bambucli.spinner import Spinner


def print_file(args):

    spinner = Spinner()

    spinner.task_in_progress("Fetching printer details")
    printer = None
    try:
        printer = get_printer(args.printer)
    except Exception as e:
        spinner.task_failed(e)
        return
    if printer is None:
        spinner.task_failed(f"Printer '{args.printer}' not found")
        print(f"Printer '{args.printer}' not found")
        return
    spinner.task_complete()

    ams_mapping = map(lambda filament: -1 if filament ==
                      'x' else filament, args.ams if args.ams else [])

    spinner.task_in_progress("Checking for ngrok token")
    ngrok_auth_token = None
    try:
        ngrok_auth_token = get_ngrok_auth_token()
    except Exception as e:
        spinner.task_failed(e)
        return
    spinner.task_complete()

    file_server, http_server = _start_tunneled_file_server(
        ngrok_auth_token, spinner)

    def on_connect(client, reason_code):
        client.print(args.file, ams_mappings=ams_mapping,
                     http_server=http_server)

    printer_monitor(printer, on_connect=on_connect)

    if file_server:
        spinner.task_in_progress(
            "Shutting down file server", lambda: asyncio.run(file_server.shutdown()))


def _start_tunneled_file_server(token, spinner):
    if token:
        spinner.task_in_progress("Starting tunneled file server")
        try:
            file_server = FileServer()
            http_server = file_server.serve(token)
            spinner.task_complete()
            return file_server, http_server
        except Exception as e:
            spinner.task_failed(e)
            return None, None
    else:
        return None, None

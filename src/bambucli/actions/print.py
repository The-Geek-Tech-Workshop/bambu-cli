import asyncio
import logging
from bambucli.bambu.messages.onpushstatus import PrintErrorCode
from bambucli.bambu.mqttclient import MqttClient
from bambucli.config import get_ngrok_auth_token, get_printer
from bambucli.fileserver import FileServer
from bambucli.printermonitor import printer_monitor
from sshkeyboard import listen_keyboard, stop_listening
import enlighten


def print_file(args):

    printer = get_printer(args.printer)
    if printer is None:
        print(f"Printer '{args.printer}' not found")
        return

    ams_mapping = map(lambda filament: -1 if filament ==
                      'x' else filament, args.ams if args.ams else [])

    ngrok_auth_token = get_ngrok_auth_token()

    file_server = FileServer() if ngrok_auth_token else None
    http_server = file_server.serve(ngrok_auth_token) if file_server else None

    def on_connect(client, reason_code):
        client.print(args.file, ams_mappings=ams_mapping,
                     http_server=http_server)

    printer_monitor(printer, on_connect=on_connect)

    asyncio.run(file_server.shutdown()) if file_server else None

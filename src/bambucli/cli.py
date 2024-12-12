import argparse
from bambucli.actions.enablengrok import enable_ngrok
from bambucli.actions.addcloud import add_cloud_printer
from bambucli.actions.login import login
from bambucli.actions.info import get_version_info
from bambucli.actions.monitor import monitor
from bambucli.actions.print import print_file
from bambucli.actions.addlocal import add_local_printer
import logging

from bambucli.actions.project import view_project
from bambucli.actions.upload import upload_file

logging.basicConfig(level=logging.INFO, filename='bambu.log',
                    datefmt='%Y-%m-%d %H:%M:%S')


def main():
    parser = argparse.ArgumentParser(
        prog='bambu',
        description='Control Bambu Printers through the command line')
    subparsers = parser.add_subparsers(required=True)

    add_local_parser = subparsers.add_parser(
        'add-local', help='Add a local printer')
    add_local_parser.set_defaults(action=add_local_printer)

    add_cloud_parser = subparsers.add_parser(
        'add-cloud', help='Add a cloud printer')
    add_cloud_parser.add_argument(
        '--email', type=str, help='Bambu Cloud email')
    add_cloud_parser.set_defaults(action=add_cloud_printer)

    print_parser = subparsers.add_parser('print', help='Print a file')
    print_parser.add_argument('printer', type=str, help='The printer to use')
    print_parser.add_argument('file', type=str, help='The file to print')
    print_parser.add_argument(
        '--ams', type=str, nargs='+', help='The AMS filament mappings')
    print_parser.set_defaults(action=print_file)

    upload_parser = subparsers.add_parser('upload', help='Upload a file')
    upload_parser.add_argument(
        'printer', type=str, help='The printer to upload to')
    upload_parser.add_argument('file', type=str, help='The file to upload')
    upload_parser.set_defaults(action=upload_file)

    info_parser = subparsers.add_parser('info', help='Get printer info')
    info_parser.add_argument(
        'printer', type=str, help='The printer to get info for')
    info_parser.set_defaults(action=get_version_info)

    login_parser = subparsers.add_parser('login', help='Login to Bambu Cloud')
    login_parser.add_argument('email', type=str, help='Bambu Cloud email')
    login_parser.add_argument('--password', type=str,
                              help='Bambu Cloud password')
    login_parser.set_defaults(action=login)

    serve_parser = subparsers.add_parser(
        'enable-ngrok', help='Allow serving of print files with ngrok')
    serve_parser.add_argument('auth_token', type=str, help='ngrok auth token')
    serve_parser.set_defaults(action=enable_ngrok)

    project_parser = subparsers.add_parser(
        'project', help='View project data')
    project_parser.add_argument('project_id', type=str, help='Project ID')
    project_parser.set_defaults(action=view_project)

    monitor_parser = subparsers.add_parser('monitor', help='Monitor a printer')
    monitor_parser.add_argument(
        'printer', type=str, help='The printer to monitor')
    monitor_parser.set_defaults(action=monitor)

    args = parser.parse_args()
    args.action(args)


if __name__ == '__main__':
    main()

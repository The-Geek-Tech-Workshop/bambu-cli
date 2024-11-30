
from bambucli.bambu.httpclient import HttpClient
from bambucli.bambu.printer import Printer
from bambucli.config import add_printer, get_cloud_account


def add_cloud_printer(args):
    account = get_cloud_account(args.email)

    if account is None:
        return

    printers = HttpClient().get_printers(account)
    for index, printer in enumerate(printers):
        print(
            f"{index + 1}: {printer.name} - {printer.model.value} - {printer.serial_number}")

    selection = input("Select a printer: ")
    try:
        selection = int(selection)
        if selection < 1 or selection > len(printers):
            raise ValueError
        add_printer(Printer(
            serial_number=printers[selection - 1].serial_number,
            name=printers[selection - 1].name,
            access_code=printers[selection - 1].access_code,
            model=printers[selection - 1].model,
            account_email=account.email,
            ip_address=args.ip_address
        ))
    except ValueError:
        print("Invalid selection")
        return
    except Exception as e:
        print(f"Failed to save printer configuration: {e}")
        return

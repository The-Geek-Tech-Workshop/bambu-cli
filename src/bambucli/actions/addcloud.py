
from bambucli.bambu.httpclient import HttpClient
from bambucli.bambu.printer import Printer
from bambucli.config import add_printer, get_cloud_account
from bambucli.spinner import Spinner


def add_cloud_printer(args):

    spinner = Spinner()

    spinner.task_in_progress("Fetching account details")
    account = get_cloud_account(args.email)

    if account is None:
        spinner.task_failed("Account not found")
        return
    spinner.task_complete()
    spinner.task_in_progress(
        f"Fetching printers for Bambu Cloud account {account.email}")
    printers = HttpClient().get_printers(account)
    spinner.task_complete()
    for index, printer in enumerate(printers):
        print(
            f"{index + 1}: {printer.name} - {printer.model.value} - {printer.serial_number}")
    selection = input("Select a printer: ")
    try:
        selection = int(selection)
        if selection < 1 or selection > len(printers):
            raise ValueError
        spinner.task_in_progress("Saving printer configuration")
        add_printer(Printer(
            serial_number=printers[selection - 1].serial_number,
            name=printers[selection - 1].name,
            access_code=printers[selection - 1].access_code,
            model=printers[selection - 1].model,
            account_email=account.email,
            ip_address=None
        ))
        spinner.task_complete()
    except ValueError:
        print("Invalid selection")
        return
    except Exception as e:
        spinner.task_failed(e)
        return

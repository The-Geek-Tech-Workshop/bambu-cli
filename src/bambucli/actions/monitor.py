
from bambucli.dashboard import dashboard
from bambucli.actions.ensureip import ensure_printer_ip_address
from bambucli.config import get_all_printers, get_printer
from bambucli.spinner import Spinner


def monitor(args):

    spinner = Spinner()
    spinner.task_in_progress("Fetching printer details")
    try:
        printers = list(map(get_printer, args.printers)
                        ) if args.printers else get_all_printers().values()
        spinner.task_complete()
    except Exception as e:
        spinner.task_failed(e)
        return

    if None in printers:
        printers_found = [
            printer.name for printer in printers if printer is not None]
        printers_not_found = [
            printer for printer in args.printers if printer not in printers_found]
        spinner.task_failed(f"1 or more printers '{
                            ", ".join(printers_not_found)}' not found")
        return

    # if printer.ip_address is None and printer.account_email is None:
    #     spinner.task_in_progress("Checking for printer ip address")
    #     try:
    #         printer = ensure_printer_ip_address(printer)
    #         spinner.task_complete()
    #     except Exception as e:
    #         spinner.task_failed(e)

    dashboard(*printers)



from bambucli.spinner import Spinner
from bambucli.strfdelta import strfdelta
from bambucli.bambu.projectfilereader import extract_project_file_data


def read_3mf_file(args):
    spinner = Spinner()
    spinner.task_in_progress("Parsing 3mf file")
    try:
        project_file = extract_project_file_data(args.file)
        spinner.task_complete()

        print(f"\nModel: {project_file.model.value}")
        print(f"Nozzle Diameter: {project_file.nozzle_diameter}")
        print(f"Filament Type: {project_file.filament_type.value}")
        print(f"Filament Amount: {project_file.filament_amount_grams}g")
        print(f"Print Time: {strfdelta(
            project_file.print_time, '{H:02}:{M:02}:{S:02}')}")
    except Exception as e:
        spinner.task_failed(e)

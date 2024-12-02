

from bambucli.bambu.httpclient import HttpClient
from bambucli.config import get_cloud_account
from bambucli.spinner import Spinner


def view_project(args):
    project_id = args.project_id

    spinner = Spinner()
    spinner.task_in_progress("Fetching account details")
    account = None
    try:
        account = get_cloud_account()
        spinner.task_complete()
    except Exception as e:
        spinner.task_failed(e)
        return

    spinner.task_in_progress("Fetching project data")
    project = None
    try:
        project = HttpClient().get_project(account, project_id)
        spinner.task_complete()
    except Exception as e:
        spinner.task_failed(e)
        return

    print(f'Project {project_id} data:')
    print(f'  Name: {project.name}')
    print(f'  Description: {project.description}')
    print(f'  Created: {project.created}')
    print(f'  Updated: {project.updated}')

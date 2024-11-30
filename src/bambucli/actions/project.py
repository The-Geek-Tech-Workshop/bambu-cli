

from bambucli.bambu.httpclient import HttpClient
from bambucli.config import get_cloud_account


def view_project(args):
    project_id = args.project_id
    account = get_cloud_account()
    project = HttpClient().get_project(account, project_id)
    print(f'Project {project_id} data:')
    print(f'  Name: {project.name}')
    print(f'  Description: {project.description}')
    print(f'  Created: {project.created}')
    print(f'  Updated: {project.updated}')

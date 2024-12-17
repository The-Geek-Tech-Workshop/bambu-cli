

from bambucli.bambu.httpclient import HttpClient
from bambucli.config import get_cloud_account


def get_tasks(args):

    account = get_cloud_account()
    http_client = HttpClient()
    (tasks, total_tasks) = http_client.get_tasks(
        account, limit=2, after=10, device_id="01P00A461300591")
    for task in tasks:
        print(f"ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Device ID: {task.deviceId}")
        print(f"Start Time: {task.startTime}")

    print(f"\nTotal tasks: {total_tasks}")

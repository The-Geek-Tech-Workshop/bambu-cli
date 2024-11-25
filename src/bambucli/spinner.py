

from rich.status import Status
from rich import print

in_progress_style = "[bold white]"
complete_style = "[bold green]"
error_style = "[bold red]"


class Spinner(Status):

    def __init__(self):
        super().__init__(status="")

    def task_in_progress(self, task_name: str):
        self.update(f"{in_progress_style}{task_name}...")

    def task_complete(self):
        print(f"{self.status} {complete_style}Done")

    def task_failed(self):
        print(f"{self.status} {error_style}Failed")

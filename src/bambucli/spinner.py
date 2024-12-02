

from typing import Optional
from rich.status import Status
from rich import print

in_progress_style = "[bold white]"
complete_style = "[bold green]"
error_style = "[bold red]"


class Spinner(Status):

    def __init__(self):
        super().__init__(status="")

    def task_in_progress(self, task_name: str, task=None):
        self.update(f"{in_progress_style}{task_name}...")
        self.start()
        if task:
            try:
                ret_value = task()
                self.task_complete()
                return True, ret_value
            except Exception as e:
                self.task_failed(str(e))
                return False, None

    def task_complete(self):
        print(f"{self.status} {complete_style}Done")
        self.stop()

    def task_failed(self, error_message: Optional[str] = None):
        print(f"{self.status} {error_style}Failed{
              f': {error_message}' if error_message else ''}")
        self.stop()

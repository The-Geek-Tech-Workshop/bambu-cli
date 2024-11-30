from socketserver import TCPServer
import threading


class SignalingTCPServer(TCPServer):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ready_event = threading.Event()

    def service_actions(self):
        self.ready_event.set()

    def serve_forever_in_thread(self):
        thread = threading.Thread(target=self.serve_forever, daemon=True)
        thread.start()
        self.ready_event.wait()
        return thread

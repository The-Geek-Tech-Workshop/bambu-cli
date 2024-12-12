import logging
from pathlib import Path
import ssl
from bambucli.ftpsimplicit import ImplicitFTP_TLS

logger = logging.getLogger(__name__)
BAMBU_FTP_USER = 'bblp'
BAMBU_FTP_PORT = 990
CACHE_DIRECTORY = 'cache/'


class FtpClient:
    def __init__(self, host, password) -> None:
        # Setup FTPS connection
        ftps = ImplicitFTP_TLS()
        ftps.context = ssl._create_unverified_context()

        def connect():
            ftps.connect(host=host, port=BAMBU_FTP_PORT)
            ftps.login(user=BAMBU_FTP_USER, passwd=password)
            ftps.prot_p()  # Set up secure data connection
        self.connect = connect
        self._ftps = ftps

    def upload_file(self, local_path: str | Path, remote_path: str | Path):
        local_file = local_path if local_path.__class__ == Path else Path(
            local_path)
        remote_file = remote_path if remote_path.__class__ == Path else Path(
            remote_path)
        if not local_file.exists():
            raise Exception(f"File {local_file} not found")

        with open(local_file, 'rb') as file_buffer:
            self._ftps.storbinary(f'STOR {remote_file}', file_buffer)

    def quit(self):
        self._ftps.quit()

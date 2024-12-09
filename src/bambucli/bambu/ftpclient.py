import logging
from pathlib import Path
import ssl
from bambucli.ftpsimplicit import ImplicitFTP_TLS

logger = logging.getLogger(__name__)
BAMBU_FTP_USER = 'bblp'
BAMBU_FTP_PORT = 990


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

    def upload_file(self, file):
        local_file = Path(file)
        if not local_file.exists():
            raise Exception(f"File {local_file} not found")

        with open(local_file, 'rb') as f:
            self._ftps.storbinary(f'STOR {local_file.name}', f)

    def quit(self):
        self._ftps.quit()

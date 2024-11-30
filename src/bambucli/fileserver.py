import asyncio
from typing import cast
import ngrok
from bambucli.signalingtcpserver import SignalingTCPServer
from http.server import SimpleHTTPRequestHandler

from ngrok.ngrok import HttpListenerBuilder


PORT = 8000


class FileServer():

    def serve(self, auth_token):
        httpd = self._create_httpd()
        listener = asyncio.run(self._create_listener(httpd, auth_token))
        httpd.serve_forever_in_thread()

        async def cleanup():
            httpd.shutdown()

        self.shutdown = cleanup
        return listener.url()

    def _create_httpd(self):
        return SignalingTCPServer(("", PORT), SimpleHTTPRequestHandler)

    async def _create_listener(self, httpd, authtoken):
        session: ngrok.Session = (
            await ngrok.SessionBuilder()
            .authtoken(authtoken)
            .connect()
        )
        listener: ngrok.Listener = (
            await session.http_endpoint()
            .scheme("HTTPS")
            .listen_and_serve(httpd)
        )
        return listener

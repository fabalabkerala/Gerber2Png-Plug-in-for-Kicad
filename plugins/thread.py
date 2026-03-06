#https://opensource.org/licenses/MIT 

import os
import webbrowser
import shutil
import wx
import tempfile
import http.server
import socketserver
import secrets
import threading
from urllib.parse import urlencode
from threading import Thread
from .result_event import *
from .config import *
from .process import *


class Gerber2PngThread(Thread):
    def __init__(self, wxObject):
        Thread.__init__(self)
        self.process = Gerber2PngProcess()
        self.wxObject = wxObject
        self.start()

    def run(self):
        
        temp_dir = tempfile.mkdtemp()
        temp_fd, temp_file = tempfile.mkstemp()
        os.close(temp_fd)

        try:
            self.report(5)

            self.process.get_gerber_file(temp_dir)

            self.report(15)

            self.process.get_netlist_file(temp_dir)

            self.report(25)

            self.process.get_components_file(temp_dir)

            self.report(35)

            gerberData = self.process.get_gerber_parameter()

            self.report(45)

            p_name = self.process.get_name()

            temp_file = shutil.make_archive(p_name, 'zip', temp_dir)
            self.report(55)

            token = secrets.token_urlsafe(16)
            server = self._create_server(temp_file, token)
            port = server.server_address[1]

            self.report(65)

            query = urlencode({
                'port': port,
                'token': token,
                'boardWidth': gerberData['boardWidth'],
                'boardHeight': gerberData['boardHeight'],
                'boardLayer': gerberData['boardLayer'],
            })
            launch_url = frontendUrl + '?' + query

            self.report(75)
            webbrowser.open(launch_url)
            self.report(85)

            # Serve exactly one download and then shutdown.
            server.serve_forever()
            self.report(100)

        except Exception as e:
            wx.MessageBox(str(e), "Error", wx.OK | wx.ICON_ERROR)
            self.report(-1)
            return
       
        self.report(-1)

    def report(self, status):
        wx.PostEvent(self.wxObject, ResultEvent(status))

    def _create_server(self, zip_file_path, token):
        allowed_origin = frontendOrigin

        class GerberHandler(http.server.BaseHTTPRequestHandler):
            def _set_cors_headers(self):
                self.send_header("Access-Control-Allow-Origin", allowed_origin)
                self.send_header("Access-Control-Allow-Methods", "GET, OPTIONS")
                self.send_header("Access-Control-Allow-Headers", "Content-Type")

            def do_OPTIONS(self):
                self.send_response(200)
                self._set_cors_headers()
                self.end_headers()

            def do_GET(self):
                if not self.path.startswith("/file"):
                    self.send_response(404)
                    self._set_cors_headers()
                    self.end_headers()
                    return

                query = self.path.split("?", 1)[-1] if "?" in self.path else ""
                params = {}
                for item in query.split("&"):
                    if "=" in item:
                        key, val = item.split("=", 1)
                        params[key] = val

                if params.get("token") != token:
                    self.send_response(403)
                    self._set_cors_headers()
                    self.end_headers()
                    self.wfile.write(b"Invalid token")
                    return

                self.send_response(200)
                self._set_cors_headers()
                self.send_header("Content-Type", "application/zip")
                self.end_headers()

                with open(zip_file_path, "rb") as f:
                    shutil.copyfileobj(f, self.wfile)

                threading.Thread(target=self.server.shutdown, daemon=True).start()

            def log_message(self, format, *args):
                return

        class OneShotTCPServer(socketserver.TCPServer):
            allow_reuse_address = True

        try:
            return OneShotTCPServer(("127.0.0.1", defaultServerPort), GerberHandler)
        except OSError:
            return OneShotTCPServer(("127.0.0.1", 0), GerberHandler)



    

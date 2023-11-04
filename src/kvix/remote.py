import http.client
import http.server
import threading
from typing import Callable
from kvix import Context

from kvix.conf import Conf
from kvix.l10n import _

listen_host_conf_title = _("Host").setup(ru_RU="Хост")
listen_port_conf_title = _("Port").setup(ru_RU="Порт")
remote_scope_title_text = _("Remote Control").setup(ru_RU="Удалённое управление")


class Configurable:
    def __init__(self, conf: Conf):
        self._conf = conf

    def _scope(self) -> Conf:
        return self._conf.scope("kvix").scope("remote").setup(title=str(remote_scope_title_text))

    def _host(self) -> str:
        item = (
            self._scope()
            .item("host")
            .setup(
                default="127.0.0.1",
                title=str(listen_host_conf_title),
                on_change=self._on_change_conf,
            )
        )
        return str(item.read())

    def _port(self) -> int:
        item = (
            self._scope()
            .item("port")
            .setup(
                default="23844",
                title=str(listen_port_conf_title),
                read_mapping=int,
                on_change=self._on_change_conf,
            )
        )
        return int(str(item.read()))

    def _on_change_conf(self) -> None:
        pass


def apply(msg, func, *args, **kwargs):
    try:
        return apply(func, *args, **kwargs)
    except Exception as e:
        raise RuntimeError(msg) from e


class Client(Configurable):
    def is_server_ready(self):
        try:
            self._http("/ping")
            return True
        except:
            return False

    def ping(self):
        self._http("/ping")

    def activate(self):
        self._http("/activate")

    def quit(self):
        self._http("/quit")

    def _http(self, path: str):
        conn = http.client.HTTPConnection(self._host() + ":" + str(self._port()))
        try:
            conn.request("POST", path)
            status = conn.getresponse().status
            body = conn.getresponse().read()
            if 2 != status / 100:
                raise RuntimeError(
                    "remote call %s failed: status %d, body %s" % (path, status, body)
                )
        except Exception as e:
            raise RuntimeError("remote call to %s failed: %s" % (path, e)) from e


class Server(Configurable):
    def __init__(self, context: Context, on_activate: Callable[[], None]):
        Configurable.__init__(self, context.conf)
        self._context = context
        self._on_activate = on_activate
        self._http_server = None

    def run(self):
        "run in this thread"
        this_server = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def do_POST(self):
                if self.path == "/ping":
                    self.response(200, "ok")
                elif self.path == "/activate":
                    try:
                        this_server._on_activate()
                        self.response(200, "ok")
                    except Exception as e:
                        self._error(e)
                elif self.path == "/quit":
                    try:
                        this_server._context.quit()
                        self.response(200, "ok")
                    except Exception as e:
                        self._error(e)
                else:
                    self.response(400, "wrong request")

            def _error(self, e: Exception | None = None):
                if e:
                    print(e)
                self.response(500, "Internal server error, see server logs for details.")

            def response(self, status: int, msg: str):
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(b'{"msg":"' + bytes(msg, "UTF-8") + b'"}')

        self._http_server = http.server.HTTPServer((self._host(), int(self._port())), Handler)
        self._http_server.serve_forever()

    def start(self):
        "start server in background"
        self.stop()
        threading.Thread(name="kvix.remote.Server", target=self.run).start()

    def stop(self):
        "stop server"
        if self._http_server:
            self._http_server.shutdown()
            self._http_server = None

    def _on_change_conf(self) -> None:
        self.start()

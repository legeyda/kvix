import http.client
import http.server
import threading
from typing import Callable
from kwix import Context

from kwix.conf import Conf
from kwix.l10n import _

listen_host_conf_title = _('Host').setup(ru_RU='Хост')
listen_port_conf_title = _('Port').setup(ru_RU='Порт')


def get_host_port(conf: Conf):
	scope = conf.scope('kwix').scope('remote')
	listen_host_conf_item = scope.item('host').setup(default = '127.0.0.1', title = str(listen_host_conf_title))
	listen_port_conf_item = scope.item('port').setup(default = '23844', title = str(listen_port_conf_title), read_mapping=int)
	return (str(listen_host_conf_item.read()), listen_port_conf_item.read())

		


class Configurable:
	def __init__(self, conf: Conf):
		self._conf = conf
	def _scope(self) -> Conf:
		return self._conf.scope('kwix').scope('remote')
	def _host(self) -> str:
		item = self._scope().item('host').setup(default = '127.0.0.1', title = str(listen_host_conf_title), on_change=self._on_change_conf)
		return str(item.read())
	def _port(self) -> int:
		item = self._scope().item('port').setup(default = '23844', title = str(listen_port_conf_title), read_mapping=int, on_change=self._on_change_conf)
		return int(str(item.read()))
	def _on_change_conf(self) -> None:
		pass





class Client(Configurable):
	def ping(self) -> bool:
		return self._http('/ping')
	def activate(self):
		if not self._http('/activate'):
			raise RuntimeError('remote activate failed')
	def quit(self):
		if not self._http('/quit'):
			raise RuntimeError('remote quit failed')
	def _http(self, path: str) -> bool:
		conn = http.client.HTTPConnection(self._host() + ':' + str(self._port()))
		try:
			conn.request("POST", path)
			return 2 == conn.getresponse().status / 100
		except:
			return False



class Server(Configurable):
	def __init__(self, context: Context, on_activate: Callable[[], None]):
		Configurable.__init__(self, context.conf)
		self._context = context
		self._on_activate = on_activate
		self._http_server = None
	def run(self):
		'run in this thread'
		this_server = self
		class Handler(http.server.BaseHTTPRequestHandler):
			def do_POST(self):
				if self.path == '/ping':
					self.response(200, 'ok')
				elif self.path == '/activate':
					try:
						this_server._on_activate()
						self.response(200, 'ok')
					except Exception as e:
						self._error(e)
				elif self.path == '/quit':
					try:
						this_server._context.quit()
						self.response(200, 'ok')
					except Exception as e:
						self._error(e)
				else:
					self.response(400, 'wrong request')
			def _error(self, e: Exception | None = None):
				if e:
					print(e)
				self.response(500, 'Internal server error, see server logs for details.')				
			def response(self, status: int, msg: str):
				self.send_response(status)
				self.send_header("Content-Type", "application/json")
				self.end_headers()
				self.wfile.write(b'{"msg":"' + bytes(msg, 'UTF-8') + b'"}')
		self._http_server = http.server.HTTPServer((self._host(), int(self._port())), Handler)
		self._http_server.serve_forever()
	def start(self):
		'start server in background'
		self.stop()
		threading.Thread(name='kwix.remote.Server', target = self.run).start()
	def stop(self):
		'stop server'
		if self._http_server:
			self._http_server.shutdown()
			self._http_server = None
	def _on_change_conf(self) -> None:
		self.start()
		

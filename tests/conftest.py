# 3rd party
import pytest
from pytest_httpserver import HTTPServer
from pytest_httpserver.pytest_plugin import Plugin, PluginHTTPServer, get_httpserver_listen_address

# this package
from tests.common import error_codes_list

pytest_plugins = ("pytest_regressions", )


@pytest.fixture(scope="session")
def httpserver_listen_address():
	return get_httpserver_listen_address()


@pytest.fixture(scope="session")
def httpserver(httpserver_listen_address):
	if Plugin.SERVER:
		Plugin.SERVER.clear()
		yield Plugin.SERVER
		return

	host, port = httpserver_listen_address
	if not host:
		host = HTTPServer.DEFAULT_LISTEN_HOST
	if not port:
		port = HTTPServer.DEFAULT_LISTEN_PORT

	server = PluginHTTPServer(host=host, port=port)
	server.start()
	yield server


@pytest.fixture(scope="session")
def error_server(httpserver: HTTPServer) -> HTTPServer:
	for status_code in error_codes_list:
		httpserver.expect_request(f"/{status_code}").respond_with_json('', status=status_code)

	return httpserver

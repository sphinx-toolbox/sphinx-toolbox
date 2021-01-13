#  Based on https://github.com/agronholm/sphinx-autodoc-typehints
#  Copyright (c) Alex Grönholm
#  MIT Licensed
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
import os
import pathlib
import shutil
import sys

# 3rd party
import pytest
from pytest_httpserver import HTTPServer  # type: ignore
from pytest_httpserver.pytest_plugin import Plugin, PluginHTTPServer, get_httpserver_listen_address  # type: ignore
from sphinx.testing.path import path
from sphobjinv import Inventory  # type: ignore

# this package
from tests.common import error_codes_list

pytest_plugins = ("pytest_regressions", "sphinx.testing.fixtures", "domdf_python_tools.testing")

collect_ignore = ["roots"]


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


@pytest.fixture(scope="session")
def inv(pytestconfig):
	cache_path = "python{v.major}.{v.minor}/objects.inv".format(v=sys.version_info)
	inv_dict = pytestconfig.cache.get(cache_path, None)
	if inv_dict is not None:
		return Inventory(inv_dict)

	print("Downloading objects.inv")
	url = "https://docs.python.org/{v.major}.{v.minor}/objects.inv".format(v=sys.version_info)
	inv = Inventory(url=url)
	pytestconfig.cache.set(cache_path, inv.json_dict())
	return inv


@pytest.fixture(autouse=True)
def _remove_sphinx_projects(sphinx_test_tempdir):
	# Remove any directory which appears to be a Sphinx project from
	# the temporary directory area.
	# See https://github.com/sphinx-doc/sphinx/issues/4040
	roots_path = pathlib.Path(sphinx_test_tempdir)
	for entry in roots_path.iterdir():
		try:
			if entry.is_dir() and pathlib.Path(entry, "_build").exists():
				shutil.rmtree(str(entry))
		except PermissionError:
			pass


@pytest.fixture()
def rootdir():
	return path(os.path.dirname(__file__) or '.').abspath() / "roots"

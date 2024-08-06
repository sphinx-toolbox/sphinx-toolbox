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
import types
from typing import Iterator, Optional, Tuple

# 3rd party
import docutils.nodes
import pytest
import sphinx.writers.html5
from domdf_python_tools.paths import PathPlus
from pytest_httpserver import HTTPServer
from pytest_httpserver.pytest_plugin import Plugin, PluginHTTPServer, get_httpserver_listen_address
from sphobjinv import Inventory  # type: ignore[import-untyped]

# this package
from tests.common import error_codes_list

if sys.version_info >= (3, 10):
	types.Union = types.UnionType

pytest_plugins = (
		"pytest_regressions",
		"sphinx.testing.fixtures",
		"coincidence",
		"sphinx_toolbox.testing",
		)

collect_ignore = ["roots"]


@pytest.fixture(scope="session")
def httpserver(httpserver_listen_address: Tuple[str, int]) -> Iterator[Optional[HTTPServer]]:
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
def httpserver_listen_address() -> Tuple[str, int]:
	return get_httpserver_listen_address()


@pytest.fixture(scope="session")
def error_server(httpserver: HTTPServer) -> HTTPServer:
	for status_code in error_codes_list:
		httpserver.expect_request(f"/{status_code:d}").respond_with_json('', status=status_code)

	return httpserver


@pytest.fixture(scope="session")
def inv(pytestconfig) -> Inventory:
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
def _remove_sphinx_projects(sphinx_test_tempdir: pathlib.Path) -> None:
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
def rootdir() -> PathPlus:
	return PathPlus(os.path.dirname(__file__) or '.').abspath() / "roots"


@pytest.fixture()
def docutils_17_compat(monkeypatch) -> None:

	def visit_section(self, node: docutils.nodes.section) -> None:
		self.section_level += 1
		self.body.append(self.starttag(node, "div", CLASS="section"))

	# self.body.append(self.starttag(node, 'section'))

	def depart_section(self, node: docutils.nodes.section) -> None:
		self.section_level -= 1
		self.body.append('</div>\n')

	def visit_figure(self, node: docutils.nodes.figure) -> None:
		atts = {"class": "figure"}

		if node.get("width"):
			atts["style"] = f"width: {node['width']}"

		atts["class"] += f" align-{node.get('align', 'default')}"

		self.body.append(self.starttag(node, "div", **atts))

	def depart_figure(self, node: docutils.nodes.figure) -> None:
		self.body.append('</div>\n')

	monkeypatch.setattr(sphinx.writers.html5.HTML5Translator, "visit_section", visit_section)
	monkeypatch.setattr(sphinx.writers.html5.HTML5Translator, "depart_section", depart_section)
	monkeypatch.setattr(sphinx.writers.html5.HTML5Translator, "visit_figure", visit_figure)
	monkeypatch.setattr(sphinx.writers.html5.HTML5Translator, "depart_figure", depart_figure)

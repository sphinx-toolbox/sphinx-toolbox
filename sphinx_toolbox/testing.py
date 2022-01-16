#!/usr/bin/env python3
#
#  testing.py
r"""
Functions for testing Sphinx extensions.

.. extras-require:: testing
	:pyproject:

.. seealso:: Sphinx's own ``testing`` library: https://github.com/sphinx-doc/sphinx/tree/3.x/sphinx/testing

.. latex:vspace:: 45px

.. _pytest-regressions: https://pypi.org/project/pytest-regressions/
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#  Based on Sphinx
#  Copyright (c) 2007-2020 by the Sphinx team.
#  |  All rights reserved.
#  |
#  |  Redistribution and use in source and binary forms, with or without
#  |  modification, are permitted provided that the following conditions are
#  |  met:
#  |
#  |  * Redistributions of source code must retain the above copyright
#  |    notice, this list of conditions and the following disclaimer.
#  |
#  |  * Redistributions in binary form must reproduce the above copyright
#  |    notice, this list of conditions and the following disclaimer in the
#  |    documentation and/or other materials provided with the distribution.
#  |
#  |  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  |  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  |  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  |  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  |  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  |  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  |  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  |  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  |  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  |  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  |  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
import copy
import sys
import tempfile
from functools import partial
from types import SimpleNamespace
from typing import Any, Callable, Dict, List, NamedTuple, Optional, Set, Tuple, Type, Union, cast

# 3rd party
import pytest  # nodep
import sphinx.application
from bs4 import BeautifulSoup  # type: ignore
from coincidence.regressions import check_file_output, check_file_regression  # nodep
from docutils import __version_info__ as docutils_version
from docutils import nodes
from docutils.parsers.rst import Directive, roles
from docutils.transforms import Transform
from domdf_python_tools.doctools import prettify_docstrings
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.typing import PathLike
from jinja2 import Template  # nodep
from pygments.lexer import Lexer  # type: ignore  # nodep
from pytest_regressions.common import check_text_files  # nodep
from pytest_regressions.file_regression import FileRegressionFixture  # nodep
from sphinx.builders import Builder
from sphinx.config import Config
from sphinx.domains import Domain, Index
from sphinx.domains.python import PythonDomain
from sphinx.environment.collectors import EnvironmentCollector
from sphinx.events import EventListener
from sphinx.events import EventManager as BaseEventManager
from sphinx.ext.autodoc.directive import AutodocDirective
from sphinx.highlighting import lexer_classes
from sphinx.registry import SphinxComponentRegistry
from sphinx.roles import XRefRole
from sphinx.util import docutils
from sphinx.util.typing import RoleFunction, TitleGetter

# this package
from sphinx_toolbox.utils import SphinxExtMetadata

__all__ = [
		"Sphinx",
		"run_setup",
		"RunSetupOutput",
		"remove_html_footer",
		"check_html_regression",
		"remove_html_link_tags",
		"check_asset_copy",
		"HTMLRegressionFixture",
		"html_regression",
		]


class FakeBuilder(Builder):
	pass


class EventManager(BaseEventManager):

	def connect(self, name: str, callback: Callable, priority: int) -> int:
		"""
		Connect a handler to specific event.
		"""

		listener_id = self.next_listener_id
		self.next_listener_id += 1
		self.listeners[name].append(EventListener(listener_id, callback, priority))
		return listener_id


class Sphinx:
	"""
	A class that pretends to be :class:`sphinx.application.Sphinx` but that is stripped
	back to allow the internals to be inspected. This can be used in tests to ensure the
	nodes, roles etc. being registered in an extension's ``setup()`` function are actually
	being registered.
	"""  # noqa: D400

	registry: SphinxComponentRegistry  #: Instance of :class:`sphinx.registry.SphinxComponentRegistry`
	config: Config  #: Instance of :class:`sphinx.config.Config`
	events: EventManager  #: Instance of :class:`sphinx.events.EventManager`
	html_themes: Dict[str, str]  #: Mapping of HTML theme names to filesystem paths.

	# builder: Builder  #: Instance of :class:`sphinx.builder.Builder`

	def __init__(self):  # , buildername: str = "html"
		self.registry = SphinxComponentRegistry()
		self.config = Config({}, {})
		self.events = EventManager(self)  # type: ignore
		self.html_themes: Dict[str, str] = {}
		# self.builder = self.registry.create_builder(self, buildername)

	def add_builder(self, builder: Type[Builder], override: bool = False) -> None:
		r"""
		Register a new builder.

		The registered values are stored in the ``app.registry.builders`` dictionary
		(:class:`typing.Dict`\[:class:`str`\, :class:`typing.Type`\[:class:`sphinx.builders.Builder`\]]).
		"""

		self.registry.add_builder(builder, override=override)

	def add_config_value(
			self,
			name: str,
			default: Any,
			rebuild: Union[bool, str],
			types: Any = (),
			) -> None:
		r"""
		Register a configuration value.

		The registered values are stored in the ``app.config.values`` dictionary
		(:class:`typing.Dict`\[:class:`str`\, :class:`typing.Tuple`]).
		"""

		if rebuild in {False, True}:
			rebuild = "env" if rebuild else ''

		self.config.add(name, default, rebuild, types)

	def add_event(self, name: str) -> None:
		r"""
		Register an event called ``name``.

		The registered values are stored in the ``app.events.events`` dictionary
		(:class:`typing.Dict`\[:class:`str`\, :class:`str`\]).
		"""

		self.events.add(name)

	def set_translator(
			self,
			name: str,
			translator_class: Type[nodes.NodeVisitor],
			override: bool = False,
			) -> None:
		r"""
		Register or override a Docutils translator class.

		The registered values are stored in the ``app.registry.translators`` dictionary.
		(:class:`typing.Dict`\[:class:`str`\, :class:`typing.Type`\[:class:`docutils.nodes.NodeVisitor`\]]).

		.. clearpage::
		"""

		self.registry.add_translator(name, translator_class, override=override)

	def add_node(
			self,
			node: Type[nodes.Element],
			override: bool = False,
			**kwargs: Tuple[Callable, Callable],
			) -> None:
		r"""
		Register a Docutils node class.

		The registered values are stored in the ``additional_nodes`` set returned by
		:func:`~sphinx_toolbox.testing.run_setup`
		(:class:`typing.Set`\[:class:`typing.Type`\[:class:`docutils.nodes.Node`\]]).
		"""

		if not override and docutils.is_node_registered(node):
			raise ValueError(
					f"node class {node.__name__!r} is already registered, its visitors will be overridden"
					)

		docutils.register_node(node)
		self.registry.add_translation_handlers(node, **kwargs)

	def add_enumerable_node(
			self,
			node: Type[nodes.Element],
			figtype: str,
			title_getter: Optional[TitleGetter] = None,
			override: bool = False,
			**kwargs: Tuple[Callable, Callable],
			) -> None:
		"""
		Register a Docutils node class as a numfig target.
		"""

		# Sphinx's signature is wrong WRT Optional
		self.registry.add_enumerable_node(
				node,
				figtype,
				title_getter,  # type: ignore
				override=override,
				)
		self.add_node(node, override=override, **kwargs)

	def add_directive(self, name: str, cls: Type[Directive], override: bool = False) -> None:
		"""
		Register a Docutils directive.
		"""

		if not override and docutils.is_directive_registered(name):
			raise ValueError(f"directive {name!r} is already registered, it will be overridden")

		docutils.register_directive(name, cls)

	def add_role(self, name: str, role: Any, override: bool = False) -> None:
		r"""
		Register a Docutils role.

		The registered values are stored in the ``roles`` dictionary returned by
		:func:`~sphinx_toolbox.testing.run_setup`.
		(:class:`typing.Dict`\[:class:`str`\, :class:`typing.Callable`\]).
		"""

		if not override and docutils.is_role_registered(name):
			raise ValueError(f"role {name!r} is already registered, it will be overridden")

		docutils.register_role(name, role)

	def add_generic_role(self, name: str, nodeclass: Any, override: bool = False) -> None:
		"""
		Register a generic Docutils role.
		"""

		if not override and docutils.is_role_registered(name):
			raise ValueError(f"role {name!r} is already registered, it will be overridden")

		role = roles.GenericRole(name, nodeclass)

		docutils.register_role(name, role)

	def add_domain(
			self,
			domain: Type[Domain],
			override: bool = False,
			) -> None:
		"""
		Register a domain.
		"""

		self.registry.add_domain(domain, override=override)

	def add_directive_to_domain(
			self,
			domain: str,
			name: str,
			cls: Type[Directive],
			override: bool = False,
			) -> None:
		"""
		Register a Docutils directive in a domain.
		"""

		self.registry.add_directive_to_domain(domain, name, cls, override=override)

	def add_role_to_domain(
			self,
			domain: str,
			name: str,
			role: Union[RoleFunction, XRefRole],
			override: bool = False,
			) -> None:
		"""
		Register a Docutils role in a domain.
		"""

		self.registry.add_role_to_domain(domain, name, role, override=override)

	def add_index_to_domain(
			self,
			domain: str,
			index: Type[Index],
			override: bool = False,
			) -> None:
		"""
		Register a custom index for a domain.
		"""

		self.registry.add_index_to_domain(domain, index)

	def add_object_type(
			self,
			directivename: str,
			rolename: str,
			indextemplate: str = '',
			parse_node: Optional[Callable] = None,
			ref_nodeclass: Optional[Type[nodes.TextElement]] = None,
			objname: str = '',
			doc_field_types: List = [],
			override: bool = False,
			) -> None:
		"""
		Register a new object type.
		"""

		# Sphinx's signature is wrong WRT Optional
		self.registry.add_object_type(
				directivename,
				rolename,
				indextemplate,
				parse_node,  # type: ignore
				ref_nodeclass,  # type: ignore
				objname,
				doc_field_types,
				override=override,
				)

	def add_crossref_type(
			self,
			directivename: str,
			rolename: str,
			indextemplate: str = '',
			ref_nodeclass: Optional[Type[nodes.TextElement]] = None,
			objname: str = '',
			override: bool = False,
			) -> None:
		"""
		Register a new crossref object type.
		"""

		# Sphinx's signature is wrong WRT Optional
		self.registry.add_crossref_type(
				directivename,
				rolename,
				indextemplate,
				ref_nodeclass,  # type: ignore
				objname,
				override=override,
				)

	def add_transform(self, transform: Type[Transform]) -> None:
		"""
		Register a Docutils transform to be applied after parsing.
		"""

		self.registry.add_transform(transform)

	def add_post_transform(self, transform: Type[Transform]) -> None:
		"""
		Register a Docutils transform to be applied before writing.
		"""

		self.registry.add_post_transform(transform)

	def add_js_file(self, filename: str, **kwargs: str) -> None:
		"""
		Register a JavaScript file to include in the HTML output.

		.. versionadded:: 2.8.0
		"""

		self.registry.add_js_file(filename, **kwargs)

	# 	if hasattr(self.builder, 'add_js_file'):
	# 		self.builder.add_js_file(filename, **kwargs)  # type: ignore
	#

	def add_css_file(self, filename: str, **kwargs: str) -> None:
		"""
		Register a stylesheet to include in the HTML output.

		.. versionadded:: 2.7.0
		"""

		self.registry.add_css_files(filename, **kwargs)

	# 	if hasattr(self.builder, 'add_css_file'):
	# 		self.builder.add_css_file(filename, **kwargs)  # type: ignore

	def add_latex_package(
			self,
			packagename: str,
			options: Optional[str] = None,
			after_hyperref: bool = False,
			) -> None:
		"""
		Register a package to include in the LaTeX source code.
		"""

		# Sphinx's signature is wrong WRT Optional
		self.registry.add_latex_package(packagename, cast(str, options), after_hyperref)

	def add_lexer(self, alias: str, lexer: Type[Lexer]) -> None:
		"""
		Register a new lexer for source code.
		"""

		if isinstance(lexer, Lexer):
			raise TypeError("app.add_lexer() API changed; Please give lexer class instead instance")
		else:
			lexer_classes[alias] = lexer

	def add_autodocumenter(self, cls: Any, override: bool = False) -> None:
		"""
		Register a new documenter class for the autodoc extension.
		"""

		self.registry.add_documenter(cls.objtype, cls)
		self.add_directive("auto" + cls.objtype, AutodocDirective, override=override)

	def add_autodoc_attrgetter(
			self,
			typ: Type,
			getter: Callable[[Any, str, Any], Any],
			) -> None:
		"""
		Register a new ``getattr``-like function for the autodoc extension.
		"""

		self.registry.add_autodoc_attrgetter(typ, getter)

	def add_source_suffix(self, suffix: str, filetype: str, override: bool = False) -> None:
		"""
		Register a suffix of source files.
		"""

		self.registry.add_source_suffix(suffix, filetype, override=override)

	def add_source_parser(self, *args: Any, **kwargs: Any) -> None:
		"""
		Register a parser class.
		"""

		self.registry.add_source_parser(*args, **kwargs)

	def add_env_collector(self, collector: Type[EnvironmentCollector]) -> None:
		"""
		No-op for now.

		.. TODO:: Make this do something
		"""

	# def add_env_collector(self, collector: Type[EnvironmentCollector]) -> None:
	# 	"""
	# 	Register an environment collector class.
	# 	"""
	#
	# 	collector().enable(self)

	def add_html_theme(self, name: str, theme_path: str) -> None:
		"""
		Register an HTML Theme.
		"""

		self.html_themes[name] = theme_path

	def add_html_math_renderer(
			self,
			name: str,
			inline_renderers: Optional[Tuple[Callable, Callable]] = None,
			block_renderers: Optional[Tuple[Callable, Callable]] = None,
			) -> None:
		"""
		Register a math renderer for HTML.
		"""

		self.registry.add_html_math_renderer(name, inline_renderers, block_renderers)  # type: ignore

	def setup_extension(self, extname: str) -> None:
		"""
		Import and setup a Sphinx extension module.

		.. TODO:: implement this
		"""

		# self.registry.load_extension(self, extname)

	def require_sphinx(self, version: str) -> None:
		"""
		Check the Sphinx version if requested.

		No-op when testing
		"""

	# event interface
	def connect(self, event: str, callback: Callable, priority: int = 500) -> int:
		"""
		Register *callback* to be called when *event* is emitted.
		"""

		listener_id = self.events.connect(event, callback, priority)
		return listener_id


@prettify_docstrings
class RunSetupOutput(NamedTuple):
	"""
	:class:`~typing.NamedTuple` representing the output from :func:`~sphinx_toolbox.testing.run_setup`.
	"""

	setup_ret: Union[None, Dict[str, Any], "SphinxExtMetadata"]  #: The output from the ``setup()`` function.
	directives: Dict[str, Callable]  #: Mapping of directive names to directive functions.
	roles: Dict[str, Callable]  #: Mapping of role names to role functions.
	additional_nodes: Set[Type[Any]]  #: Set of custom docutils nodes registered in ``setup()``.
	app: Sphinx  #: Instance of :class:`sphinx_toolbox.testing.Sphinx`.


_sphinx_dict_setup = Callable[[sphinx.application.Sphinx], Optional[Dict[str, Any]]]
_sphinx_metadata_setup = Callable[[sphinx.application.Sphinx], Optional["SphinxExtMetadata"]]
_fake_dict_setup = Callable[[Sphinx], Optional[Dict[str, Any]]]
_fake_metadata_setup = Callable[[Sphinx], Optional["SphinxExtMetadata"]]
_setup_func_type = Union[_sphinx_dict_setup, _sphinx_metadata_setup, _fake_dict_setup, _fake_metadata_setup]


def run_setup(setup_func: _setup_func_type) -> RunSetupOutput:  # , buildername: str = "html"
	"""
	Function for running an extension's ``setup()`` function for testing.

	:param setup_func: The ``setup()`` function under test.

	:returns: 5-element namedtuple

	.. clearpage::
	"""

	app = Sphinx()  # buildername

	app.add_domain(PythonDomain)

	_additional_nodes = copy.copy(docutils.additional_nodes)
	try:
		sphinx.util.docutils.additional_nodes = set()

		with docutils.docutils_namespace():
			setup_ret = setup_func(app)  # type: ignore
			directives = copy.copy(docutils.directives._directives)  # type: ignore
			roles = copy.copy(docutils.roles._roles)  # type: ignore
			additional_nodes = copy.copy(docutils.additional_nodes)
	finally:
		docutils.additional_nodes = _additional_nodes

	return RunSetupOutput(setup_ret, directives, roles, additional_nodes, app)


def remove_html_footer(page: BeautifulSoup) -> BeautifulSoup:
	"""
	Remove the Sphinx footer from HTML pages.

	The footer contains the Sphinx and theme versions and therefore changes between versions.
	This can cause unwanted, false positive test failures.

	:param page: The page to remove the footer from.

	:return: The page without the footer.
	"""

	for div in page.select("div.footer"):
		div.extract()

	return page


def remove_html_link_tags(page: BeautifulSoup) -> BeautifulSoup:
	"""
	Remove link tags from HTML pages.

	These may vary between different versions of Sphinx and its extensions.
	This can cause unwanted, false positive test failures.

	:param page: The page to remove the link tags from.

	:return: The page without the link tags.

	.. clearpage::
	"""

	for div in page.select("head link"):
		div.extract()

	return page


def check_html_regression(page: BeautifulSoup, file_regression: FileRegressionFixture):
	"""
	Check an HTML page generated by Sphinx for regressions, using `pytest-regressions`_.

	:param page: The page to test.
	:param file_regression: The file regression fixture.

	**Example usage**

	.. code-block:: python

		@pytest.mark.parametrize("page", ["index.html"], indirect=True)
		def test_page(page: BeautifulSoup, file_regression: FileRegressionFixture):
			check_html_regression(page, file_regression)
	"""  # noqa: RST306

	__tracebackhide__ = True

	page = remove_html_footer(page)
	page = remove_html_link_tags(page)

	for div in page.select("script"):
		if "_static/language_data.js" in str(div):
			div.extract()

	for div in page.select("div.sphinxsidebar"):
		div.extract()

	check_file_regression(
			StringList(page.prettify()),
			file_regression,
			extension=".html",
			)


class HTMLRegressionFixture(FileRegressionFixture):
	"""
	Subclass of :class:`pytest_regressions.file_regression.FileRegressionFixture` for checking HTML files.

	.. versionadded:: 2.0.0
	"""

	def check(  # type: ignore
		self,
		page: BeautifulSoup,
		*,
		extension: str = ".html",
		jinja2: bool = False,
		**kwargs
		):
		r"""
		Check an HTML page generated by Sphinx for regressions, using `pytest-regressions`_.

		:param page: The page to test.
		:param jinja2: Whether to render the reference file as a jinja2 template.
		:param \*\*kwargs: Additional keyword arguments passed to
			:meth:`pytest_regressions.file_regression.FileRegressionFixture.check`.

		.. versionchanged:: 2.14.0  Added the ``jinja2`` keyword argument.

		When ``jinja2`` is :py:obj:`True`, the reference file will be rendered as a jinja2 template.
		The template is passed the following variables:

		* ``sphinx_version`` -- the Sphinx version number, as a tuple of integers.
		* ``python_version`` -- the Python version number, in the form returned by :data:`sys.version_info`.
		* ``docutils_version`` -- the docutils version number, as a tuple of integers (*New in version 2.16.0*).

		**Example usage**

		.. code-block:: python

			@pytest.mark.parametrize("page", ["index.html"], indirect=True)
			def test_page(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
				html_regression.check(page, file_regression)
		"""  # noqa: RST306

		__tracebackhide__ = True

		page = remove_html_footer(page)
		page = remove_html_link_tags(page)

		for div in page.select("script"):
			if "_static/language_data.js" in str(div):
				div.extract()

		for div in page.select("div.sphinxsidebar"):
			div.extract()

		if sphinx.version_info >= (4, 3):  # pragma: no cover
			for div in page.select("span.w"):
				div.extract()
			for div in page.select("span.p"):
				if div.string == '=':
					sibling = div.next_sibling
					div.replace_with('')
					sibling.replace_with(f"= {sibling.text}")

		kwargs.pop("encoding", None)
		kwargs.pop("extension", None)

		if jinja2:

			def check_fn(obtained_filename, expected_filename):
				__tracebackhide__ = True

				expected_filename = PathPlus(expected_filename)
				template = Template(expected_filename.read_text())

				expected_filename.write_text(
						template.render(
								sphinx_version=sphinx.version_info,
								python_version=sys.version_info,
								docutils_version=docutils_version,
								)
						)

				return check_text_files(obtained_filename, expected_filename, encoding="UTF-8")

		else:
			check_fn = partial(check_text_files, encoding="UTF-8")

		super().check(
				str(StringList(page.prettify())),
				encoding="UTF-8",
				extension=extension,
				check_fn=check_fn,
				)


@pytest.fixture()
def html_regression(datadir, original_datadir, request) -> HTMLRegressionFixture:
	"""
	Returns an :class:`~.HTMLRegressionFixture` scoped to the test function.

	.. versionadded:: 2.0.0
	"""

	return HTMLRegressionFixture(datadir, original_datadir, request)


def check_asset_copy(
		func: Callable[[sphinx.application.Sphinx, Exception], Any],
		*asset_files: PathLike,
		file_regression: FileRegressionFixture,
		):
	r"""
	Helper to test functions which respond to Sphinx ``build-finished`` events and copy asset files.

	.. versionadded:: 2.0.0

	:param func: The function to test.
	:param \*asset_files: The paths of asset files copied by the function, relative to the Sphinx output directory.
	:param file_regression:
	"""

	__tracebackhide__ = True

	with tempfile.TemporaryDirectory() as tmpdir:
		tmp_pathplus = PathPlus(tmpdir)

		fake_app = SimpleNamespace()
		fake_app.builder = SimpleNamespace()
		fake_app.builder.format = "html"
		fake_app.outdir = fake_app.builder.outdir = tmp_pathplus

		func(fake_app, None)  # type: ignore

		for filename in asset_files:
			filename = tmp_pathplus / filename

			check_file_output(filename, file_regression, extension=f"_{filename.stem}{filename.suffix}")

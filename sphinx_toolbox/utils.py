#!/usr/bin/env python3
#
#  utils.py
"""
General utility functions.
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
#  singleton function based on attrs
#  https://github.com/python-attrs/attrs
#  Copyright (c) 2015 Hynek Schlawack
#  MIT Licensed
#

# stdlib
import functools
import re
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Pattern, Set, Tuple, Type, TypeVar, cast

# 3rd party
import sphinx.config
from apeye.url import RequestsURL
from docutils.nodes import Node
from domdf_python_tools.doctools import prettify_docstrings
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.errors import PycodeError
from sphinx.ext.autodoc import Documenter, logger
from sphinx.locale import __
from sphinx.pycode import ModuleAnalyzer
from typing_extensions import TypedDict

__all__ = [
		"add_nbsp_substitution",
		"allow_subclass_add",
		"baseclass_is_private",
		"begin_generate",
		"code_repr",
		"escape_trailing__",
		"filter_members_warning",
		"flag",
		"get_first_matching",
		"GITHUB_COM",
		"is_namedtuple",
		"make_github_url",
		"metadata_add_version",
		"NoMatchError",
		"OptionSpec",
		"Param",
		"parse_parameters",
		"Purger",
		"SetupFunc",
		"SphinxExtMetadata",
		"typed_flag_regex",
		"typed_param_regex",
		"unknown_module_warning",
		"untyped_param_regex",
		]

#: Instance of :class:`apeye.url.RequestsURL` that points to the GitHub website.
GITHUB_COM: RequestsURL = RequestsURL("https://github.com")

#: Type hint for the ``option_spec`` variable of Docutils directives.
OptionSpec = Mapping[str, Callable[[str], Any]]

_T = TypeVar("_T")


@functools.lru_cache()
def make_github_url(username: str, repository: str) -> RequestsURL:
	"""
	Construct a URL to a GitHub repository from a username and repository name.

	:param username: The username of the GitHub account that owns the repository.
	:param repository: The name of the repository.
	"""

	return GITHUB_COM / username / repository


def flag(argument: Any) -> bool:
	"""
	Check for a valid flag option (no argument) and return :py:obj:`True`.

	Used in the ``option_spec`` of directives.

	.. seealso::

		:class:`docutils.parsers.rst.directives.flag`, which returns :py:obj:`None` instead of :py:obj:`True`.

	:raises: :exc:`ValueError` if an argument is given.
	"""

	if argument and argument.strip():
		raise ValueError(f"No argument is allowed; {argument!r} supplied")
	else:
		return True


@prettify_docstrings
class Purger:
	"""
	Class to purge redundant nodes.

	:param attr_name: The name of the build environment's attribute that stores the list of nodes,
		e.g. ``all_installation_nodes``.
	"""

	def __init__(self, attr_name: str):
		self.attr_name = str(attr_name)

	def __repr__(self) -> str:
		return f"{self.__class__.__name__}({self.attr_name!r})"

	def purge_nodes(  # pragma: no cover
			self,
			app: Sphinx,
			env: BuildEnvironment,
			docname: str,
			) -> None:
		"""
		Remove all redundant nodes.

		This function can be configured for the :event:`env-purge-doc` event:

		.. code-block::

			my_node_purger = Purger("all_my_node_nodes")

			def setup(app: Sphinx):
				app.connect("env-purge-doc", my_node_purger.purge_nodes)

		:param app: The Sphinx application.
		:param env: The Sphinx build environment.
		:param docname: The name of the document to remove nodes for.
		"""

		if not hasattr(env, self.attr_name):
			return

		all_nodes = [todo for todo in getattr(env, self.attr_name) if todo["docname"] != docname]
		setattr(env, self.attr_name, all_nodes)

	def get_outdated_docnames(
			self,
			app: Sphinx,
			env: BuildEnvironment,
			added: Set[str],
			changed: Set[str],
			removed: Set[str],
			) -> List[str]:
		"""
		Returns a list of all docnames containing one or more nodes this :class:`~.Purger` is aware of.

		This function can be configured for the :event:`env-get-outdated` event:

		.. code-block::

			my_node_purger = Purger("all_my_node_nodes")

			def setup(app: Sphinx):
				app.connect("env-get-outdated", my_node_purger.get_outdated_docnames)

		.. versionadded:: 2.7.0

		:param app: The Sphinx application.
		:param env: The Sphinx build environment.
		:param added: A set of newly added documents.
		:param changed: A set of document names whose content has changed.
		:param removed: A set of document names which have been removed.
		"""

		if not hasattr(env, self.attr_name):
			return []

		return list({todo["docname"] for todo in getattr(env, self.attr_name)})

	def add_node(self, env: BuildEnvironment, node: Node, targetnode: Node, lineno: int):
		"""
		Add a node.

		:param env: The Sphinx build environment.
		:param node:
		:param targetnode:
		:param lineno:
		"""

		if not hasattr(env, self.attr_name):
			setattr(env, self.attr_name, [])

		all_nodes = getattr(env, self.attr_name)

		all_nodes.append({
				"docname": env.docname,
				"lineno": lineno,
				"installation_node": node.deepcopy(),
				"target": targetnode,
				})


def singleton(name: str) -> object:
	"""
	Factory function to return a string singleton.

	:param name: The name of the singleton.
	"""

	name = str(name)

	class Singleton:
		_singleton = None

		def __new__(cls):
			if Singleton._singleton is None:
				Singleton._singleton = super().__new__(cls)
			return Singleton._singleton

		def __repr__(self) -> str:
			return name

		def __str__(self) -> str:
			return name

	Singleton.__name__ = name
	Singleton.__doc__ = f"Singleton {name}"
	return Singleton()


no_default = singleton("no_default")


class NoMatchError(ValueError):
	"""
	Raised when no matching values were found in :func:`~.get_first_matching`.

	.. versionadded:: 0.7.0
	"""


def get_first_matching(
		condition: Callable[[Any], bool],
		iterable: Iterable[_T],
		default: _T = no_default,  # type: ignore
		) -> _T:
	"""
	Returns the first value in ``iterable`` that meets ``condition``, or ``default`` if none match.

	.. versionadded:: 0.7.0

	:param condition: The condition to evaluate.
	:param iterable:
	:param default: The default value to return if no values in ``iterable`` match.
	"""

	if default is not no_default:
		if not condition(default):
			raise ValueError("The condition must evaluate to True for the default value.")

		iterable = [*iterable, default]

	for match in iterable:
		if condition(match):
			return match

	raise NoMatchError(f"No matching values for '{condition}' in {iterable}")


def escape_trailing__(string: str) -> str:
	"""
	Returns the given string with trailing underscores escaped to prevent Sphinx treating them as references.

	.. versionadded:: 0.8.0

	:param string:
	"""

	if string.endswith('_'):
		return f"{string[:-1]}\\_"
	return string


def code_repr(obj: Any) -> str:
	"""
	Returns the repr of the given object as reStructuredText inline code.

	.. versionadded:: 0.9.0

	:param obj:
	"""

	return f"``{obj!r}``"


class SphinxExtMetadata(TypedDict, total=False):
	"""
	:class:`typing.TypedDict` representing the metadata dictionary returned by
	Sphinx extensions' ``setup`` functions.

	This is treated by Sphinx as metadata of the extension.
	"""  # noqa: D400

	version: str
	"""
	A string that identifies the extension version.

	It is used for extension version requirement checking and informational purposes.

	If not given, ``'unknown version'`` is substituted.
	"""

	env_version: int
	"""
	An integer that identifies the version of env data structure if the extension stores any data to environment.

	It is used to detect the data structure has been changed from last build.
	Extensions have to increment the version when data structure has changed.

	If not given, Sphinx considers the extension does not stores any data to environment.
	"""

	parallel_read_safe: bool
	"""
	A boolean that specifies if parallel reading of source files can be used when the extension is loaded.

	It defaults to :py:obj:`False`, i.e. you have to explicitly specify your extension
	to be parallel-read-safe after checking that it is.
	"""

	parallel_write_safe: bool
	"""
	A boolean that specifies if parallel writing of output files can be used when the extension is loaded.

	Since extensions usually don’t negatively influence the process, this defaults to :py:obj:`True`.
	"""


SetupFunc = Callable[[Sphinx], Optional["SphinxExtMetadata"]]
"""
Type annotation for Sphinx extensions' ``setup`` functions.

.. versionadded:: 1.9.0
"""


def begin_generate(
		documenter: Documenter,
		real_modname: Optional[str] = None,
		check_module: bool = False,
		) -> Optional[str]:
	"""
	Boilerplate for the top of ``generate`` in :class:`sphinx.ext.autodoc.Documenter` subclasses.

	.. versionadded:: 0.2.0

	:param documenter:
	:param real_modname:
	:param check_module:

	:return: The ``sourcename``, or :py:obj:`None` if certain conditions are met,
		to indicate that the Documenter class should exit early.
	"""

	# Do not pass real_modname and use the name from the __module__
	# attribute of the class.
	# If a class gets imported into the module real_modname
	# the analyzer won't find the source of the class, if
	# it looks in real_modname.

	if not documenter.parse_name():
		# need a module to import
		unknown_module_warning(documenter)
		return None

	# now, import the module and get object to document
	if not documenter.import_object():
		return None

	# If there is no real module defined, figure out which to use.
	# The real module is used in the module analyzer to look up the module
	# where the attribute documentation would actually be found in.
	# This is used for situations where you have a module that collects the
	# functions and classes of internal submodules.
	guess_modname = documenter.get_real_modname()
	documenter.real_modname = real_modname or guess_modname

	# try to also get a source code analyzer for attribute docs
	try:
		documenter.analyzer = ModuleAnalyzer.for_module(documenter.real_modname)
		# parse right now, to get PycodeErrors on parsing (results will
		# be cached anyway)
		documenter.analyzer.find_attr_docs()

	except PycodeError as err:
		logger.debug("[autodoc] module analyzer failed: %s", err)
		# no source file -- e.g. for builtin and C modules
		documenter.analyzer = None  # type: ignore
		# at least add the module.__file__ as a dependency
		if hasattr(documenter.module, "__file__") and documenter.module.__file__:
			documenter.directive.filename_set.add(documenter.module.__file__)
	else:
		documenter.directive.filename_set.add(documenter.analyzer.srcname)

	if documenter.real_modname != guess_modname:
		# Add module to dependency list if target object is defined in other module.
		try:
			analyzer = ModuleAnalyzer.for_module(guess_modname)
			documenter.directive.filename_set.add(analyzer.srcname)
		except PycodeError:
			pass

	# check __module__ of object (for members not given explicitly)
	if check_module:
		if not documenter.check_module():
			return None

	sourcename = documenter.get_sourcename()

	# make sure that the result starts with an empty line.  This is
	# necessary for some situations where another directive preprocesses
	# reST and no starting newline is present
	documenter.add_line('', sourcename)

	return sourcename


def unknown_module_warning(documenter: Documenter) -> None:
	"""
	Log a warning that the module to import the object from is unknown.

	.. versionadded:: 0.2.0

	:param documenter:
	"""

	msg = __(
			"don't know which module to import for autodocumenting %r "
			'(try placing a "module" or "currentmodule" directive in the document, '
			"or giving an explicit module name)"
			)

	logger.warning(msg % documenter.name, type="autodoc")


def filter_members_warning(member, exception: Exception) -> None:
	"""
	Log a warning when filtering members.

	.. versionadded:: 0.2.0

	:param member:
	:param exception:
	"""

	logger.warning(
			__("autodoc: failed to determine %r to be documented, the following exception was raised:\n%s"),
			member,
			exception,
			type="autodoc"
			)


class Param(TypedDict):
	"""
	:class:`~typing.TypedDict` to represent a parameter parsed from a class or function's docstring.

	.. versionadded:: 0.8.0
	"""

	#: The docstring of the parameter.
	doc: List[str]

	#: The type of the parameter.
	type: str  # noqa A003


_identifier_pattern = r"[A-Za-z_]\w*"

typed_param_regex: Pattern[str] = re.compile(
		fr"^:(param|parameter|arg|argument)\s*({_identifier_pattern}\s+)({_identifier_pattern}\s*):\s*(.*)",
		flags=re.ASCII,
		)
"""
Regex to match ``:param <type> <name>: <docstring>`` flags.

.. versionadded:: 0.8.0
"""

untyped_param_regex: Pattern[str] = re.compile(
		fr"^:(param|parameter|arg|argument)\s*({_identifier_pattern}\s*):\s*(.*)",
		flags=re.ASCII,
		)
"""
Regex to match ``:param <name>: <docstring>`` flags.

.. versionadded:: 0.8.0
"""

typed_flag_regex: Pattern[str] = re.compile(
		fr"^:(paramtype|type)\s*({_identifier_pattern}\s*):\s*(.*)",
		flags=re.ASCII,
		)
"""
Regex to match ``:type <name>: <type>`` flags.

.. versionadded:: 0.8.0
"""


def parse_parameters(lines: List[str], tab_size: int = 8) -> Tuple[Dict[str, Param], List[str], List[str]]:
	"""
	Parse parameters from the docstring of a class/function.

	.. versionadded:: 0.8.0

	:param lines: The lines of the docstring
	:param tab_size:

	:return: A mapping of parameter names to their docstrings and types, a list of docstring lines that
		appeared before the parameters, and the list of docstring lines that appear after the parameters.

	.. clearpage::
	"""

	a_tab = ' ' * tab_size

	params: Dict[str, Param] = {}
	last_arg: Optional[str] = None

	pre_output: List[str] = []
	post_output: List[str] = []

	def add_empty(param_name: str):
		if param_name not in params:
			params[param_name] = {"doc": [], "type": ''}

	for line in lines:

		if post_output:
			post_output.append(line)
			continue

		typed_m = typed_param_regex.match(line)
		untyped_m = untyped_param_regex.match(line)
		type_only_m = typed_flag_regex.match(line)

		if typed_m:
			last_arg = typed_m.group(3).strip()
			add_empty(cast(str, last_arg))
			params[last_arg]["doc"] = [typed_m.group(4)]
			params[last_arg]["type"] = typed_m.group(2).strip()

		elif untyped_m:
			last_arg = untyped_m.group(2).strip()
			add_empty(cast(str, last_arg))
			params[last_arg]["doc"] = [untyped_m.group(3)]

		elif type_only_m:
			add_empty(type_only_m.group(2))
			params[type_only_m.group(2)]["type"] = type_only_m.group(3)

		elif line.startswith(a_tab) and last_arg is not None:
			params[last_arg]["doc"].append(line)

		elif last_arg is None:
			pre_output.append(line)

		else:
			post_output.append(line)

	return params, pre_output, post_output


def is_namedtuple(obj: Any) -> bool:
	"""
	Returns whether the given object is a :func:`collections.namedtuple` class.

	.. versionadded:: 0.8.0

	:param obj:
	"""

	return isinstance(obj, type) and issubclass(obj, tuple) and hasattr(obj, "_fields")


def allow_subclass_add(app: Sphinx, *documenters: Type[Documenter]):
	"""
	Add the given autodocumenters, but only if a subclass of it is not already registered.

	This allows other libraries to extend the autodocumenters.

	.. versionadded:: 0.8.0

	:param app: The Sphinx application.
	:param documenters:
	"""

	for cls in documenters:
		existing_documenter = app.registry.documenters.get(cls.objtype)
		if existing_documenter is None or not issubclass(existing_documenter, cls):
			app.add_autodocumenter(cls, override=True)


def baseclass_is_private(obj: Type) -> bool:
	"""
	Returns :py:obj:`True` if the first and only base class starts with a double underscore.

	:param obj:
	"""

	if hasattr(obj, "__bases__") and len(obj.__bases__) == 1:
		return obj.__bases__[0].__name__.startswith("__")
	return False


def metadata_add_version(func: SetupFunc) -> SetupFunc:
	"""
	Internal decorator for Sphinx ``setup`` functions to add the ``sphinx-toolbox``
	version number to the returned metadata dict.

	.. versionadded:: 1.9.0

	:param func:
	"""  # noqa: D400

	@functools.wraps(func)
	def wrapper(app: Sphinx):

		# this package
		from sphinx_toolbox import __version__

		ret = func(app) or {}
		ret["version"] = __version__
		return ret

	return wrapper


def add_nbsp_substitution(config: sphinx.config.Config):
	"""
	Adds the ``|nbsp|`` substitution directive to the reStructuredText prolog.

	.. versionadded:: 2.1.0

	:param config:
	"""

	nbsp_sub = ".. |nbsp| unicode:: 0xA0\n   :trim:"

	if not config.rst_prolog:
		config.rst_prolog = ''  # type: ignore

	if nbsp_sub not in config.rst_prolog:
		config.rst_prolog = '\n'.join([config.rst_prolog, '', nbsp_sub])  # type: ignore

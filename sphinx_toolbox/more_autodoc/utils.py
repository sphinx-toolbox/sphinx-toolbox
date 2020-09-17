#!/usr/bin/env python3
#
#  utils.py
"""
Helpers for writing extensions to autodoc.

.. versionadded:: 0.2.0

.. versionchanged:: 0.6.0

	Moved from :mod:`sphinx_toolbox.autodoc_helpers`.
"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#  Parts based on https://github.com/sphinx-doc/sphinx
#  |  Copyright (c) 2007-2020 by the Sphinx team (see AUTHORS file).
#  |  BSD Licensed
#  |  All rights reserved.
#  |
#  |  Redistribution and use in source and binary forms, with or without
#  |  modification, are permitted provided that the following conditions are
#  |  met:
#  |
#  |  * Redistributions of source code must retain the above copyright
#  |   notice, this list of conditions and the following disclaimer.
#  |
#  |  * Redistributions in binary form must reproduce the above copyright
#  |   notice, this list of conditions and the following disclaimer in the
#  |   documentation and/or other materials provided with the distribution.
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
import re
from typing import Any, Dict, List, Optional, Pattern, Tuple, Type, cast

# 3rd party
from sphinx.application import Sphinx
from sphinx.errors import PycodeError
from sphinx.ext.autodoc import Documenter, logger
from sphinx.locale import __
from sphinx.pycode import ModuleAnalyzer
from typing_extensions import TypedDict

__all__ = [
		"begin_generate",
		"unknown_module_warning",
		"filter_members_warning",
		"is_namedtuple",
		"parse_parameters",
		"Param",
		"typed_param_regex",
		"untyped_param_regex",
		"typed_flag_regex",
		"allow_subclass_add",
		]


def begin_generate(
		documenter: Documenter,
		real_modname: Optional[str] = None,
		check_module: bool = False,
		) -> Optional[str]:
	"""
	Boilerplate for the top of ``generate`` in :class:`sphinx.ext.autodoc.Documenter` subclasses.

	:param documenter:
	:param real_modname:
	:param check_module:

	:return: The ``sourcename``, or :py:obj:`None` if certain conditions are met,
		to indicate that the Documenter class should exit early.

	.. versionadded:: 0.2.0
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
		documenter.analyzer = ModuleAnalyzer.for_module(documenter.real_modname)  # type: ignore
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

	:param documenter:

	.. versionadded:: 0.2.0
	"""

	logger.warning(
			__(
					"don't know which module to import for autodocumenting "
					'%r (try placing a "module" or "currentmodule" directive '
					"in the document, or giving an explicit module name)"
					) % documenter.name,
			type="autodoc"
			)


def filter_members_warning(member, exception: Exception) -> None:
	"""
	Log a warning when filtering members.

	:param member:
	:param exception:

	.. versionadded:: 0.2.0
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
	type: str


typed_param_regex: Pattern = re.compile(
		r"^:(param|parameter|arg|argument)\s*([A-Za-z_]+\s+)([A-Za-z_]+\s*):\s*(.*)"
		)
"""
Regex to match ``:param <type> <name>: <docstring>`` flags.

.. versionadded:: 0.8.0
"""

untyped_param_regex: Pattern = re.compile(r"^:(param|parameter|arg|argument)\s*([A-Za-z_]+\s*):\s*(.*)")
"""
Regex to match ``:param <name>: <docstring>`` flags.

.. versionadded:: 0.8.0
"""

typed_flag_regex: Pattern = re.compile(r"^:(paramtype|type)\s*([A-Za-z_]+\s*):\s*(.*)")
"""
Regex to match ``:type <name>: <type>`` flags.

.. versionadded:: 0.8.0
"""


def parse_parameters(lines: List[str], tab_size: int = 8) -> Tuple[Dict[str, Param], List[str], List[str]]:
	"""

	:param lines: The lines of the docstring
	:param tab_size:

	:return: A dictionary mapping parameter names to their docstrings and types, a list of docstring lines that
		appeared before the parameters, and the list of docstring lines that appear after the parameters.

	.. versionadded:: 0.8.0
	"""

	a_tab = " " * tab_size

	params: Dict[str, Param] = {}
	last_arg: Optional[str] = None

	pre_output: List[str] = []
	post_output: List[str] = []

	def add_empty(param_name: str):
		if param_name not in params:
			params[param_name] = {"doc": [], "type": ''}

	for line in lines:
		typed_m = typed_param_regex.match(line)
		untyped_m = untyped_param_regex.match(line)
		type_only_m = typed_flag_regex.match(line)

		if typed_m:
			last_arg = typed_m.group(3).strip()
			add_empty(cast(str, last_arg))
			params[last_arg]["doc"] = [typed_m.group(4)]  # type: ignore
			params[last_arg]["type"] = typed_m.group(2).strip()  # type: ignore

		elif untyped_m:
			last_arg = untyped_m.group(2).strip()
			add_empty(cast(str, last_arg))
			params[last_arg]["doc"] = [untyped_m.group(3)]  # type: ignore

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
	Returns whether the given class is a :class:`collections.namedtuple`.

	:param obj:

	.. versionadded:: 0.8.0
	"""

	return isinstance(obj, type) and issubclass(obj, tuple) and hasattr(obj, "_fields")


def allow_subclass_add(app: Sphinx, *documenters: Type[Documenter]):
	"""
	Add the given autodocumenters, but only if a subclass of it is not
	already registered.

	This allows other libraries to extend the autodocumenters.

	:param app:
	:param documenters:

	.. versionadded:: 0.8.0
	"""

	for cls in documenters:
		existing_documenter = app.registry.documenters.get(cls.objtype)
		print(existing_documenter)
		if existing_documenter is None or not issubclass(existing_documenter, cls):
			app.add_autodocumenter(cls, override=True)

#!/usr/bin/env python3
#
#  autodoc_helpers.py
"""
Helpers for writing extensions to autodoc.

.. versionadded:: 0.2.0
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

# stdlib
from typing import Optional

# 3rd party
from sphinx.errors import PycodeError
from sphinx.ext.autodoc import Documenter, logger
from sphinx.locale import __
from sphinx.pycode import ModuleAnalyzer

__all__ = ["begin_generate", "unknown_module_warning", "filter_members_warning"]


def begin_generate(
		documenter: Documenter,
		real_modname: Optional[str] = None,
		check_module: bool = False,
		) -> Optional[str]:
	"""
	Boilerplate for the top of ``generate`` in :class:`EnumDocumenter` and :class:`EnumMemberDocumenter`.

	:param documenter:
	:param real_modname:
	:param check_module:

	:return: The ``sourcename``, or None if certain conditions are met,
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

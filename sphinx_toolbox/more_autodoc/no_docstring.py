#!/usr/bin/env python3
#
#  no_docstring.py
"""
Adds the ``:no-docstring:`` option to automodule directives to exclude the docstring from the output.

.. versionadded:: 1.0.0
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
from types import ModuleType
from typing import List

# 3rd party
import autodocsumm  # type: ignore
import sphinx.ext.autodoc
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, flag, metadata_add_version

__all__ = ["automodule_add_nodocstring", "no_docstring_process_docstring", "setup"]


def automodule_add_nodocstring(app) -> None:
	"""
	Add the ``:no-docstring:`` option to automodule directives to exclude the docstring from the output.

	:param app: The Sphinx app.

	.. versionchanged:: 1.0.0

		Moved from ``sphinx_toolbox.more_autodoc.__init__.py``
	"""

	sphinx.ext.autodoc.ModuleDocumenter.option_spec["no-docstring"] = flag
	autodocsumm.AutoSummModuleDocumenter.option_spec["no-docstring"] = flag

	app.setup_extension("sphinx.ext.autodoc")
	app.connect("autodoc-process-docstring", no_docstring_process_docstring, priority=1000)


def no_docstring_process_docstring(
		app: Sphinx,
		what,
		name: str,
		obj,
		options,
		lines: List[str],
		):
	"""
	Process the docstring of a module, and remove its docstring of the ``:no-docstring:`` flag was set..

	:param app: The Sphinx app
	:param what:
	:param name: The name of the object being documented
	:param obj: The object being documented.
	:param options: Mapping of autodoc options to values.
	:param lines: List of strings representing the current contents of the docstring.

	.. versionchanged:: 1.0.0

		Moved from ``sphinx_toolbox.more_autodoc.__init__.py``
	"""

	if isinstance(obj, ModuleType):
		no_docstring = options.get("no-docstring", False)
		if no_docstring:
			lines.clear()


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.no_docstring`.

	:param app: The Sphinx app.
	"""

	automodule_add_nodocstring(app)

	return {"parallel_read_safe": True}

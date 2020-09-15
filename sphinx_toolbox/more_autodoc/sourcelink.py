#!/usr/bin/env python3
#
#  sourcelink.py
"""
Show a link to the corresponding source code at the top of :rst:dir:`automodule` output.

.. versionadded:: 0.6.0
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
from typing import Any, Dict, List

# 3rd party
from sphinx.application import Sphinx

__all__ = ["sourcelinks_process_docstring", "setup"]


def sourcelinks_process_docstring(
		app: Sphinx,
		what,
		name: str,
		obj,
		options,
		lines: List[str],
		):
	"""
	Process the docstring of a module and add a link to the source code if given in the configuration.

	:param app: The Sphinx app
	:param what:
	:param name: The name of the object being documented
	:param obj: The object being documented.
	:param options: Mapping of autodoc options to values.
	:param lines: List of strings representing the current contents of the docstring.
	"""

	if (
			isinstance(obj, ModuleType) and what == "module" and app.config.autodoc_show_sourcelink  # type: ignore
			and obj.__file__.endswith(".py")
			):
		lines.insert(0, f"**Source code:** :source:`{name.replace('.', '/')}.py`")
		lines.insert(1, '')
		lines.insert(2, "--------------------")
		lines.insert(3, '')


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.sourcelink`.

	:param app: The Sphinx app.
	"""

	# this package
	from sphinx_toolbox import __version__

	app.setup_extension("sphinx_toolbox.source")
	app.setup_extension("sphinx.ext.autodoc")

	app.connect("autodoc-process-docstring", sourcelinks_process_docstring)
	app.add_config_value("autodoc_show_sourcelink", False, "env", [bool])

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

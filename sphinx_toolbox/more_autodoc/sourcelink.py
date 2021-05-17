#!/usr/bin/env python3
#
#  sourcelink.py
r"""
Show a link to the corresponding source code at the top of :rst:dir:`automodule` output.

.. versionadded:: 0.6.0
.. extensions:: sphinx_toolbox.more_autodoc.sourcelink


Configuration
----------------

.. raw:: latex

	\begin{flushleft}

:mod:`sphinx_toolbox.more_autodoc.sourcelink` can be configured using the :confval:`autodoc_default_options`
option in ``conf.py``, or with the :rst:dir:`:sourcelink: <sourcelink>` option flag to :rst:dir:`automodule`.

.. raw:: latex

	\end{flushleft}


.. confval:: autodoc_show_sourcelink
	:type: :class:`bool`
	:default: :py:obj:`False`

	If :py:obj:`True`, shows a link to the corresponding source code
	at the top of each :rst:dir:`automodule` directive.

.. rst:directive:option:: sourcelink

	When passed as an option flag to an :rst:dir:`automodule` directive,
	show a link to the corresponding source code at the top of the output *for that module only*.


.. versionchanged:: 1.1.0

	Added support for the :rst:dir:`:sourcelink: <sourcelink>` option flag to :rst:dir:`automodule`.


API Reference
--------------


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

# stdlib
from types import ModuleType
from typing import Any, List, Mapping

# 3rd party
import autodocsumm  # type: ignore
import sphinx.ext.autodoc
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, flag, metadata_add_version

__all__ = ["sourcelinks_process_docstring", "setup"]


def sourcelinks_process_docstring(
		app: Sphinx,
		what,
		name: str,
		obj,
		options: Mapping[str, Any],
		lines: List[str],
		):
	"""
	Process the docstring of a module and add a link to the source code if given in the configuration.

	:param app: The Sphinx application.
	:param what:
	:param name: The name of the object being documented.
	:param obj: The object being documented.
	:param options: Mapping of autodoc options to values.
	:param lines: List of strings representing the current contents of the docstring.
	"""

	show_sourcelink = options.get("sourcelink", app.config.autodoc_show_sourcelink)  # type: ignore

	if isinstance(obj, ModuleType) and what == "module" and obj.__file__.endswith(".py") and show_sourcelink:
		lines_to_insert = [
				".. rst-class:: source-link",
				'',
				f"    **Source code:** :source:`{name.replace('.', '/')}.py`",
				'',
				"--------------------",
				'',
				]

		for line in reversed(lines_to_insert):
			lines.insert(0, line)


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.sourcelink`.

	:param app: The Sphinx application.
	"""

	sphinx.ext.autodoc.ModuleDocumenter.option_spec["sourcelink"] = flag
	autodocsumm.AutoSummModuleDocumenter.option_spec["sourcelink"] = flag

	app.setup_extension("sphinx_toolbox.source")
	app.setup_extension("sphinx_toolbox._css")
	app.setup_extension("sphinx.ext.autodoc")

	app.connect("autodoc-process-docstring", sourcelinks_process_docstring)
	app.add_config_value("autodoc_show_sourcelink", False, "env", [bool])

	return {"parallel_read_safe": True}

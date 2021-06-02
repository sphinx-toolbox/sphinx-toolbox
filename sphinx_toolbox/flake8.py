#!/usr/bin/env python3
#
#  flake8.py
r"""
A Sphinx directive for documenting flake8 codes.

.. versionadded:: 1.6.0
.. extensions:: sphinx_toolbox.flake8


Usage
------

.. rst:directive:: .. flake8-codes:: plugin

	Adds a table documenting a flake8 plugin's codes.

	The directive takes a single argument -- the fully qualified name of the flake8 plugin module.

	Codes to document are given in the body of the directive.


	.. latex:vspace:: 10px

	**Example**

	.. raw:: latex

		\begin{multicols}{2}

	.. rest-example::

		.. flake8-codes:: flake8_dunder_all

			DALL000

	.. raw:: latex

		\end{multicols}

API Reference
----------------
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
import warnings
from typing import List, Sequence, Tuple

# 3rd party
import tabulate
from docutils import nodes
from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.ext.autodoc.importer import import_module
from sphinx.util.docutils import SphinxDirective

# this package
from sphinx_toolbox.utils import Purger, SphinxExtMetadata, metadata_add_version

__all__ = ["Flake8CodesDirective", "setup"]

table_node_purger = Purger("all_flake8_code_table_nodes")


class Flake8CodesDirective(SphinxDirective):
	"""
	A Sphinx directive for documenting flake8 codes.
	"""

	has_content: bool = True

	# the fully qualified name of the flake8 plugin module
	required_arguments: int = 1

	def run(self) -> Sequence[nodes.Node]:  # type: ignore
		"""
		Process the content of the directive.
		"""

		plugin: str = self.arguments[0]

		if not self.content:
			warnings.warn("No codes specified")
			return []

		module = import_module(plugin)
		codes: List[Tuple[str, str]] = []

		for code in self.content:
			if code.strip():
				try:
					description = getattr(module, code)
					if description.startswith(code):
						description = description[len(code):]
					codes.append((code, description.strip()))
				except AttributeError:
					warnings.warn(f"No such code {code!r}")

		if not codes:
			warnings.warn("No codes specified")
			return []

		targetid = f'flake8codes-{self.env.new_serialno("flake8codes"):d}'
		targetnode = nodes.section(ids=[targetid])

		table = tabulate.tabulate(codes, headers=["Code", "Description"], tablefmt="rst")
		content = '\n' + table.replace('\t', "    ") + '\n'

		view = StringList(content.split('\n'))
		table_node = nodes.paragraph(rawsource=content)
		self.state.nested_parse(view, self.content_offset, table_node)

		table_node_purger.add_node(self.env, table_node, targetnode, self.lineno)

		return [table_node]


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.flake8`.

	:param app: The Sphinx application.
	"""

	app.add_directive("flake8-codes", Flake8CodesDirective)
	app.connect("env-purge-doc", table_node_purger.purge_nodes)

	return {"parallel_read_safe": True}

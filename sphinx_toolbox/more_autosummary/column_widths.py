#!/usr/bin/env python3
#
#  column_widths.py
"""
Sphinx extension to allow customisation of column widths in autosummary tables with the LaTeX builder.

.. versionadded:: 3.0.0


Usage
--------------

This extension provides the :rst:dir:`autosummary-widths` directive.
This sets the autosummary table's column widths with the LaTeX builder
until the end of the current reStructuredText document,
or until the next :rst:dir:`autosummary-widths` directive.

.. rst:directive:: autosummary-widths

	Set the width of the autosummary table's columns with the LaTeX builder.

	The directive takes up to two arguments -- the column widths as vulgar fractions (e.g. ``5/10``).
	If only one argument is provided, this sets the width of the first column,
	and the width of the second column is calculated from it.
	If both arguments are provided, they set the width of the first and second columns respectively.

	:bold-title:`Examples:`

	.. code-block:: rst

		.. autosummary-widths:: 5/10
		.. autosummary-widths:: 3/10, 7/10
		.. autosummary-widths:: 35/100

	.. attention:: This directive ignores the :confval:`autosummary_col_type` configuration option.


API Reference
----------------


"""
#  Copyright © 2022 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#  Parts based on https://github.com/sphinx-doc/sphinx/blob/3.x/sphinx/ext/autosummary/__init__.py
#  |  Copyright (c) 2007-2022 by the Sphinx team (see AUTHORS file).
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
from contextlib import suppress
from fractions import Fraction
from itertools import chain
from typing import Iterable, List, Tuple, cast

# 3rd party
from docutils import nodes
from docutils.statemachine import StringList
from domdf_python_tools import stringlist
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.ext.autosummary import autosummary_table
from sphinx.util import rst
from sphinx.util.docutils import SphinxDirective, switch_source_input

# this package
from sphinx_toolbox import latex
from sphinx_toolbox.more_autosummary import PatchedAutosummary
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["AutosummaryWidths", "WidthsDirective", "configure", "setup"]


class AutosummaryWidths(PatchedAutosummary):
	"""
	Customised :rst:dir:`autosummary` directive with customisable width with the LaTeX builder.

	.. attention:: This directive ignores the :confval:`autosummary_col_type` configuration option.
	"""

	def get_table(self, items: List[Tuple[str, str, str, str]]) -> List[nodes.Node]:
		"""
		Generate a proper list of table nodes for autosummary:: directive.

		:param items: A list produced by ``self.get_items``.
		"""

		table_spec = addnodes.tabular_col_spec()

		widths = tuple(chain.from_iterable(getattr(self.state.document, "autosummary_widths", ((1, 2), (1, 2)))))
		assert len(widths) == 4

		table_spec["spec"] = r'\Xx{%d}{%d}\Xx{%d}{%d}' % widths

		table = autosummary_table('')
		real_table = nodes.table('', classes=["autosummary", "longtable"])
		table.append(real_table)

		group = nodes.tgroup('', cols=2)
		real_table.append(group)

		group.append(nodes.colspec('', colwidth=10))
		group.append(nodes.colspec('', colwidth=90))

		body = nodes.tbody('')
		group.append(body)

		def append_row(*column_texts: str) -> None:
			row = nodes.row('')
			source, line = self.state_machine.get_source_and_line()

			for text in column_texts:
				node = nodes.paragraph('')
				vl = StringList()
				vl.append(text, f"{source}:{line:d}:<autosummary>")

				with switch_source_input(self.state, vl):
					self.state.nested_parse(vl, 0, node)

					with suppress(IndexError):
						if isinstance(node[0], nodes.paragraph):
							node = node[0]

					row.append(nodes.entry('', node))

			body.append(row)

		for name, sig, summary, real_name in items:
			col1 = f":obj:`{name} <{real_name}>`"

			if "nosignatures" not in self.options:
				col1 += f"\\ {rst.escape(sig)}"

			append_row(col1, summary)

		return [table_spec, table]


class WidthsDirective(SphinxDirective):
	"""
	Sphinx directive which configures the column widths of an :rst:dir:`autosummary` table
	for the remainder of the document, or until the next `autosummary-widths` directive.
	"""  # noqa: D400

	required_arguments = 1
	optional_arguments = 1

	@staticmethod
	def parse_widths(raw_widths: Iterable[str]) -> List[Tuple[int, int]]:
		"""
		Parse a width string (as a vulgar fraction) into a list of 2-element ``(numerator, denominator)`` tuples.

		For example, ``'5/10'`` becomes ``(5, 10)``.

		:param raw_widths:
		"""

		widths = [cast(Tuple[int, int], tuple(map(int, arg.split('/')))) for arg in raw_widths]

		if len(widths) == 1:
			left_width = Fraction(*widths[0])
			right_width = 1 - left_width
			widths.append((right_width.numerator, right_width.denominator))

		return widths

	def run(self) -> List:
		"""
		Process the directive's arguments.
		"""

		self.state.document.autosummary_widths = self.parse_widths(self.arguments)  # type: ignore

		return []


def configure(app: Sphinx, config: Config):
	"""
	Configure :mod:`sphinx_toolbox.more_autosummary.column_widths`.

	:param app: The Sphinx application.
	:param config:
	"""

	latex_elements = getattr(config, "latex_elements", {})

	latex_preamble = stringlist.StringList(latex_elements.get("preamble", ''))
	latex_preamble.blankline()
	latex_preamble.append(r"\makeatletter")
	latex_preamble.append(r"\newcolumntype{\Xx}[2]{>{\raggedright\arraybackslash}p{\dimexpr")
	latex_preamble.append(r"    (\linewidth-\arrayrulewidth)*#1/#2-\tw@\tabcolsep-\arrayrulewidth\relax}}")
	latex_preamble.append(r"\makeatother")
	latex_preamble.blankline()

	latex_elements["preamble"] = str(latex_preamble)
	config.latex_elements = latex_elements  # type: ignore


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autosummary.column_widths`.

	:param app: The Sphinx application.
	"""

	app.setup_extension("sphinx_toolbox.more_autosummary")

	app.add_directive("autosummary", AutosummaryWidths, override=True)
	app.add_directive("autosummary-widths", WidthsDirective)

	app.connect("config-inited", configure)
	app.connect("build-finished", latex.replace_unknown_unicode)

	return {"parallel_read_safe": True}

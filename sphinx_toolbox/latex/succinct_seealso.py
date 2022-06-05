#!/usr/bin/env python3
#
#  succinct_seealso.py
"""
Sphinx extension which customises :rst:dir:`seealso` directives to be on one line with the LaTeX builder.

.. extensions:: sphinx_toolbox.latex.succinct_seealso

.. versionadded:: 3.0.0
"""
#
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

# 3rd party
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import admonitionlabels
from sphinx.writers.latex import LaTeXTranslator

__all__ = ("setup", )

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version


def visit_seealso(translator: LaTeXTranslator, node: addnodes.seealso) -> None:
	"""
	Visit an :class:`addnodes.seealso`` node.

	:param translator:
	:param node:
	"""

	# translator.body.append('\n\n\\begin{description}\\item[{%s:}] \\leavevmode' % admonitionlabels['seealso'])
	# translator.body.append('\n\n\\sphinxstrong{%s:} ' % admonitionlabels["seealso"])
	if len(node) > 1:
		LaTeXTranslator.visit_seealso(translator, node)
	else:
		translator.body.append('\n\n\\sphinxstrong{%s:} ' % admonitionlabels["seealso"])


def depart_seealso(translator: LaTeXTranslator, node: addnodes.seealso) -> None:
	"""
	Depart an :class:`addnodes.seealso`` node.

	:param translator:
	:param node:
	"""

	# translator.body.append("\\end{description}\n\n")
	translator.body.append("\n\n")


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.latex.succinct_seealso`.

	:param app: The Sphinx application.
	"""

	app.add_node(addnodes.seealso, latex=(visit_seealso, depart_seealso), override=True)

	return {"parallel_read_safe": True}

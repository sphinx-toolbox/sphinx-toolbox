#!/usr/bin/env python3
#
#  latex_layout.py
r"""
Makes minor adjustments to the LaTeX layout.

* Increases the whitespace above function signatures by 5px,
  to prevent the function visually merging with the previous one.
* Remove unnecessary indentation and allow "raggedright" for the fields in
  the body of functions, which prevents ugly whitespace and line breaks.
* Disables justification for function signatures.
  This is a backport of changes from Sphinx 4 added in :github:pull:`8997 <sphinx-doc/sphinx>`.

  .. versionadded:: 2.12.0

* With Sphinx 3.5, doesn't add ``\sphinxAtStartPar`` before every paragraph.
  The change in :github:issue:`8781 <sphinx-doc/sphinx>` was to solve an issue with *tables*,
  but it isn't clear why it then gets added for *every* paragraph so this extension removes it.

  .. versionadded:: 2.13.0

* Configures hyperref to apply correct page numbering to the frontmatter.

  .. versionadded:: 2.14.0


.. versionadded:: 2.10.0
.. extensions:: sphinx_toolbox.tweaks.latex_layout

-----

"""
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.builders.latex.nodes import footnotetext
from sphinx.config import Config
from sphinx.writers.latex import LaTeXTranslator

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["setup"]


def visit_desc(translator: LaTeXTranslator, node: addnodes.desc) -> None:
	translator.body.append('\n\n\\vspace{5px}')
	LaTeXTranslator.visit_desc(translator, node)


def visit_field_list(translator: LaTeXTranslator, node: nodes.field_list) -> None:
	translator.body.append('\\vspace{10px}\\begin{flushleft}\\begin{description}\n')
	if translator.table:  # pragma: no cover
		translator.table.has_problematic = True


def depart_field_list(translator: LaTeXTranslator, node: nodes.field_list) -> None:
	translator.body.append('\\end{description}\\end{flushleft}\\vspace{10px}\n')


def configure(app: Sphinx, config: Config):
	"""
	Configure Sphinx Extension.

	:param app: The Sphinx application.
	:param config:
	"""

	if not hasattr(config, "latex_elements"):  # pragma: no cover
		config.latex_elements = {}  # type: ignore

	latex_elements = (config.latex_elements or {})

	latex_preamble = latex_elements.get("preamble", '')

	# Backported from Sphinx 4
	# See https://github.com/sphinx-doc/sphinx/pull/8997
	config.latex_elements["preamble"] = '\n'.join([
			latex_preamble,
			r"\makeatletter",
			'',
			r"\renewcommand{\py@sigparams}[2]{%",
			r"  \parbox[t]{\py@argswidth}{\raggedright #1\sphinxcode{)}#2\strut}%",
			"  % final strut is to help get correct vertical separation in case of multi-line",
			"  % box with the item contents.",
			'}',
			r"\makeatother",
			])

	config.latex_elements["hyperref"] = '\n'.join([
			r"% Include hyperref last.",
			r"\usepackage[pdfpagelabels,hyperindex,hyperfigures]{hyperref}",
			r"% Fix anchor placement for figures with captions.",
			r"\usepackage{hypcap}% it must be loaded after hyperref.",
			])

	config.latex_elements["maketitle"] = '\n'.join([
			r"\begingroup",
			r"\let\oldthepage\thepage",
			r"\renewcommand{\thepage}{T\oldthepage}",
			config.latex_elements.get("maketitle", r"\sphinxmaketitle"),
			r"\endgroup"
			])


def visit_paragraph(translator: LaTeXTranslator, node: nodes.paragraph) -> None:
	index = node.parent.index(node)
	if (
			index > 0 and isinstance(node.parent, nodes.compound)
			and not isinstance(node.parent[index - 1], nodes.paragraph)
			and not isinstance(node.parent[index - 1], nodes.compound)
			):
		# insert blank line, if the paragraph follows a non-paragraph node in a compound
		translator.body.append("\\noindent\n")
	elif index == 1 and isinstance(node.parent, (nodes.footnote, footnotetext)):
		# don't insert blank line, if the paragraph is second child of a footnote
		# (first one is label node)
		pass
	else:
		# Sphinx 3.5 adds \sphinxAtStartPar here, but I don't see what it gains.
		translator.body.append('\n')


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.tweaks.latex_layout`.

	:param app: The Sphinx application.
	"""

	app.connect("config-inited", configure, priority=500)

	app.add_node(addnodes.desc, latex=(visit_desc, LaTeXTranslator.depart_desc), override=True)
	app.add_node(nodes.field_list, latex=(visit_field_list, depart_field_list), override=True)
	app.add_node(nodes.paragraph, latex=(visit_paragraph, LaTeXTranslator.depart_paragraph), override=True)

	return {"parallel_read_safe": True}

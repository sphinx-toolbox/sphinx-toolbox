#!/usr/bin/env python3
#
#  latex.py
"""
Sphinx utilities for LaTeX builders.

.. versionadded:: 2.8.0

In addition to the developer API (see below), :mod:`sphinx_toolbox.latex`
configures Sphinx to use the LaTeX footmisc_ package for symbol footnotes,
which ensures they are handled correctly.

.. _footmisc: https://ctan.org/pkg/footmisc

.. extensions:: sphinx_toolbox.latex
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

# stdlib
from typing import cast

# 3rd party
from docutils import nodes
from domdf_python_tools.stringlist import DelimitedList
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.writers.latex import LaTeXTranslator

__all__ = ["use_package", "visit_footnote", "depart_footnote", "configure", "setup"]

footmisc_symbols = ['0', '*', '†', '‡', '§', '¶', '‖', "**", "††", "‡‡"]


def visit_footnote(translator: LaTeXTranslator, node: nodes.footnote) -> None:
	"""
	Visit a :class:`docutils.nodes.footnote` node with the LaTeX translator.

	Unlike the default ``visit_footnote`` function, this one handles footnotes using symbols.

	.. versionadded:: 2.8.0

	:param translator:
	:param node:
	"""

	translator.in_footnote += 1
	footnote_id = str(cast(nodes.label, node[0]).astext())

	if not footnote_id.isnumeric():
		if footnote_id in footmisc_symbols:
			footnote_id = str(footmisc_symbols.index(footnote_id))

	if not translator.in_parsed_literal:
		translator.body.append("%\n")

	translator.body.append(rf"\begin{{footnote}}[{footnote_id}]")
	translator.body.append("\\sphinxAtStartFootnote\n")


def depart_footnote(translator: LaTeXTranslator, node: nodes.footnote) -> None:
	"""
	Depart a :class:`docutils.nodes.footnote` node with the LaTeX translator.

	.. versionadded:: 2.8.0

	:param translator:
	:param node:
	"""

	if not translator.in_parsed_literal:
		translator.body.append("%\n")

	translator.body.append(r"\end{footnote}")
	translator.in_footnote -= 1


def use_package(package: str, config: Config, *args: str, **kwargs: str) -> None:
	r"""
	Configure LaTeX to use the given package.

	The ``\usepackage`` entry is added to the
	:py:obj:`sphinx.config.Config.latex_elements` ``["preamble"]`` attribute.

	:param package:
	:param config:
	:param \*args:
	:param \*\*kwargs:
	"""

	options: DelimitedList[str] = DelimitedList()
	options.extend(args)
	options.extend(map("{}={}".format, kwargs.items()))

	use_string = rf"\usepackage[{options:,}]{{{package}}}"

	if not hasattr(config, "latex_elements") or not config.latex_elements:  # pragma: no cover
		config.latex_elements = {}  # type: ignore

	latex_preamble = config.latex_elements.get("preamble", '')

	if use_string not in latex_preamble:
		config.latex_elements["preamble"] = f"{latex_preamble}\n{use_string}"


def configure(app: Sphinx, config: Config):
	"""
	Configure :mod:`sphinx_toolbox.latex`.

	:param app: The Sphinx application.
	:param config:
	"""

	use_package("footmisc", config, "symbol")


def setup(app: Sphinx):
	"""
	Setup :mod:`sphinx_toolbox.latex`.

	.. versionadded:: 2.8.0

	:param app: The Sphinx application.
	"""

	app.add_node(nodes.footnote, latex=(visit_footnote, depart_footnote), override=True)
	app.connect("config-inited", configure)

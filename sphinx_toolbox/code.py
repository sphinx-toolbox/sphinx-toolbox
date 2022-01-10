#!/usr/bin/env python3
#
#  code.py
"""
Customised ``.. code-block::`` directive with an adjustable indent size.

.. extensions:: sphinx_toolbox.code


Usage
------

.. rst:directive:: .. code-block:: [language]
                   .. sourcecode:: [language]

	Customised ``.. code-block::`` directive with an adjustable indent size.

	.. rst:directive:option:: tab-width: width
		:type: integer

		Sets the size of the indentation in spaces.


	All other options from :rst:dir:`sphinx:code-block` are available,
	see the `Sphinx documentation`_ for details.

	.. _Sphinx documentation: https://www.sphinx-doc.org/en/3.x/usage/restructuredtext/directives.html#directive-code-block

	**Examples**

	.. rest-example::

		.. code-block:: python

			def print(text):
				sys.stdout.write(text)


	.. rest-example::

		.. code-block:: python
			:tab-width: 8

			def print(text):
				sys.stdout.write(text)

.. clearpage::

.. rst:directive:: .. code-cell:: [language]
				   .. output-cell:: [language]

	Customised ``.. code-block::`` directives which display an execution count to
	the left of the code block, similar to a Jupyter Notebook cell.

	.. versionadded:: 2.6.0

	.. rst:directive:option:: execution-count: count
		:type: positive integer

		The execution count of the cell.

	All other options from the :rst:dir:`code-block` directive above are available.

	**Examples**

	.. rest-example::

		.. code-cell:: python
			:execution-count: 1

			def print(text):
				sys.stdout.write(text)

			print("hello world")

		.. output-cell::
			:execution-count: 1

			hello world


	.. rest-example::

		.. code-cell:: python
			:execution-count: 2
			:tab-width: 8

			def print(text):
				sys.stdout.write(text)


	.. seealso::

		`nbsphinx <https://nbsphinx.readthedocs.io/en/0.8.3/>`_,
		which inspired these directives and provides additional functionality
		for integrating Jupyter Notebooks with Sphinx.

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
#  Based on Sphinx
#  Copyright (c) 2007-2020 by the Sphinx team.
#  |  All rights reserved.
#  |
#  |  Redistribution and use in source and binary forms, with or without
#  |  modification, are permitted provided that the following conditions are
#  |  met:
#  |
#  |  * Redistributions of source code must retain the above copyright
#  |    notice, this list of conditions and the following disclaimer.
#  |
#  |  * Redistributions in binary form must reproduce the above copyright
#  |    notice, this list of conditions and the following disclaimer in the
#  |    documentation and/or other materials provided with the distribution.
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
from typing import List, MutableMapping, Optional

# 3rd party
import dict2css
import docutils.nodes
import docutils.statemachine
import sphinx.directives.code
from docutils.nodes import Node
from docutils.parsers.rst import directives
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.utils import convert_indents
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.writers.html import HTMLTranslator
from sphinx.writers.latex import LaTeXTranslator

# this package
from sphinx_toolbox.utils import OptionSpec, SphinxExtMetadata, metadata_add_version

__all__ = [
		"CodeBlock",
		"CodeCell",
		"OutputCell",
		"Prompt",
		"visit_prompt_html",
		"visit_prompt_latex",
		"copy_asset_files",
		"configure",
		"setup",
		]


class CodeBlock(sphinx.directives.code.CodeBlock):
	"""
	Directive for a code block with special highlighting or line numbering settings.

	The indent_size can be adjusted with the ``:tab-width: <int>`` option.

	.. autoclasssumm:: CodeBlock
		:autosummary-sections: ;;
	"""

	option_spec: OptionSpec = {  # type: ignore
		"force": directives.flag,
		"linenos": directives.flag,
		"tab-width": int,
		"dedent": int,
		"lineno-start": int,
		"emphasize-lines": directives.unchanged_required,
		"caption": directives.unchanged_required,
		"class": directives.class_option,
		"name": directives.unchanged,
		}

	def run(self) -> List[Node]:
		"""
		Process the content of the code block.
		"""

		code = '\n'.join(self.content)

		if "tab-width" in self.options:
			tab_width = self.options["tab-width"]
		else:
			tab_width = 4

		code = convert_indents(code, tab_width=tab_width, from_=' ' * self.config.docutils_tab_width)

		self.content = docutils.statemachine.StringList(code.split('\n'))

		return super().run()


class Prompt(docutils.nodes.General, docutils.nodes.FixedTextElement):
	"""
	Represents a cell prompt for a :class:`CodeCell` and :class:`OutputCell`.

	.. versionadded:: 2.6.0
	"""


class CodeCell(CodeBlock):
	"""
	Customised code block which displays an execution count to the left of the code block,
	similar to a Jupyter Notebook cell.

	The indent_size can be adjusted with the ``:tab-width: <int>`` option.

	The execution count can be set using the ``:execution-count: <int>`` option.

	.. autoclasssumm:: CodeCell
		:autosummary-sections: ;;

	.. versionadded:: 2.6.0
	"""  # noqa: D400

	option_spec: OptionSpec = {
			**CodeBlock.option_spec,
			"execution-count": directives.positive_int,
			}

	_prompt: str = "In [%s]:"
	_class: str = "code-cell"

	def run(self) -> List[Node]:
		"""
		Process the content of the code block.
		"""

		self.options.setdefault("class", [])
		self.options["class"].append(f"{self._class}-code")

		prompt = self._prompt % self.options.get("execution-count", ' ')

		outer_node = docutils.nodes.container(classes=[self._class])

		outer_node += Prompt(
				prompt,
				prompt,
				language="none",
				classes=["prompt", f"{self._class}-prompt"],
				)

		outer_node += super().run()[0]

		return [outer_node]


class OutputCell(CodeCell):
	"""
	Variant of :class:`~.CodeCell` for displaying the output of a cell in a Jupyter Notebook.

	The indent_size can be adjusted with the ``:tab-width: <int>`` option.

	The execution count can be set using the ``:execution-count: <int>`` option.

	.. versionadded:: 2.6.0

	.. autoclasssumm:: OutputCell
		:autosummary-sections: ;;
	"""

	_prompt: str = "[%s]:"
	_class: str = "output-cell"


def visit_prompt_html(translator: HTMLTranslator, node: Prompt) -> None:
	"""
	Visit a :class:`~.Prompt` node with the HTML translator.

	.. versionadded:: 2.6.0

	:param translator:
	:param node:
	"""

	starttag = translator.starttag(node, "div", suffix='', CLASS="notranslate")
	translator.body.append(starttag + node.rawsource + '</div>\n')
	raise docutils.nodes.SkipNode


def visit_prompt_latex(translator: LaTeXTranslator, node: Prompt) -> None:
	"""
	Visit a :class:`~.Prompt` node with the LaTeX translator.

	.. versionadded:: 2.6.0

	:param translator:
	:param node:
	"""

	translator.body.append("\n\n")
	translator.body.append(r"\vspace{4mm}")

	if f"code-cell-prompt" in node["classes"]:
		colour = "nbsphinxin"
	elif f"output-cell-prompt" in node["classes"]:
		colour = "nbsphinxout"
	else:  # pragma: no cover
		colour = "black"

	translator.body.append(
			rf"\llap{{\color{{{colour}}}\texttt{{{node.rawsource}}}"
			r"\,\hspace{\fboxrule}\hspace{\fboxrule}\hspace{\fboxsep}}"
			)
	translator.body.append(r"\vspace{-7mm}")

	raise docutils.nodes.SkipNode


def copy_asset_files(app: Sphinx, exception: Optional[Exception] = None):
	"""
	Copy additional stylesheets into the HTML build directory.

	.. versionadded:: 2.6.0

	:param app: The Sphinx application.
	:param exception: Any exception which occurred and caused Sphinx to abort.
	"""

	if exception:  # pragma: no cover
		return

	if app.builder is None or app.builder.format.lower() != "html":  # pragma: no cover
		return

	prompt_style: dict2css.Style = {
			"user-select": None,
			"font-size": "13px",
			"font-family": '"SFMono-Regular", Menlo, Consolas, Monaco, Liberation Mono, Lucida Console, monospace',
			"border": None,
			"padding": "11px 0 0",
			"margin": "0 5px 0 0",
			"box-shadow": None,
			"wrap-option": None,
			"white-space": "nowrap",
			}

	container_style: dict2css.Style = {
			"padding-top": "5px",
			"display": "flex",
			"align-items": "stretch",
			"margin": 0,
			}

	code_style_string = "div.code-cell.container div.code-cell-code, div.output-cell.container div.output-cell-code"
	code_style: dict2css.Style = {
			"width": "100%",
			"padding-top": 0,
			"margin-top": 0,
			}

	style: MutableMapping[str, dict2css.Style] = {
			"div.code-cell.container div.prompt": {"color": "#307FC1"},
			"div.output-cell.container div.prompt": {"color": "#BF5B3D"},
			"div.code-cell.container div.prompt, div.output-cell.container div.prompt": prompt_style,
			"div.code-cell.container, div.output-cell.container": container_style,
			code_style_string: code_style,
			}

	static_dir = PathPlus(app.outdir) / "_static"
	static_dir.maybe_make(parents=True)
	dict2css.dump(style, static_dir / "sphinx-toolbox-code.css")


def configure(app: Sphinx, config: Config):
	"""
	Configure :mod:`sphinx_toolbox.code`.

	.. versionadded:: 2.9.0

	:param app: The Sphinx application.
	:param config:
	"""

	latex_elements = getattr(config, "latex_elements", {})

	latex_preamble = StringList(latex_elements.get("preamble", ''))
	latex_preamble.blankline()
	latex_preamble.append(r"\definecolor{nbsphinxin}{HTML}{307FC1}")
	latex_preamble.append(r"\definecolor{nbsphinxout}{HTML}{BF5B3D}")

	latex_elements["preamble"] = str(latex_preamble)
	config.latex_elements = latex_elements  # type: ignore


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.code`.

	.. versionadded:: 1.0.0

	:param app: The Sphinx application.
	"""

	# Code block with customisable indent size.
	app.add_directive("code-block", CodeBlock, override=True)
	app.add_directive("sourcecode", CodeBlock, override=True)

	app.add_directive("code-cell", CodeCell)
	app.add_directive("output-cell", OutputCell)

	# Hack to get the docutils tab size, as there doesn't appear to be any other way
	app.setup_extension("sphinx_toolbox.tweaks.tabsize")

	app.add_node(
			Prompt,
			html=(visit_prompt_html, lambda *args, **kwargs: None),
			latex=(visit_prompt_latex, lambda *args, **kwargs: None)
			)

	app.connect("config-inited", configure)
	app.add_css_file("sphinx-toolbox-code.css")
	app.connect("build-finished", copy_asset_files)

	return {"parallel_read_safe": True}

#!/usr/bin/env python3
#
#  latex.py
r"""
Sphinx utilities for LaTeX builders.

.. versionadded:: 2.8.0

In addition to the developer API (see below), :mod:`sphinx_toolbox.latex`
configures Sphinx to use the LaTeX footmisc_ package for symbol footnotes,
which ensures they are handled correctly.

.. _footmisc: https://ctan.org/pkg/footmisc

.. extensions:: sphinx_toolbox.latex

Usage
-------

.. raw:: latex

	\begin{multicols}{2}

.. rst:directive:: latex:samepage
                   samepage

	Configures LaTeX to make all content within this directive appear on the same page.

	This can be useful to avoid awkward page breaks.

	This directive has no effect with non-LaTeX builders.

	.. versionadded:: 2.9.0


.. rst:directive:: latex:clearpage
                   clearpage

	Configures LaTeX to start a new page.

	This directive has no effect with non-LaTeX builders.

	.. versionadded:: 2.10.0
	.. seealso:: :rst:dir:`latex:cleardoublepage`


.. rst:directive:: latex:cleardoublepage
                   cleardoublepage

	Configures LaTeX to start a new page.

	In a two-sided printing it also makes the next page a right-hand (odd-numbered) page,
	inserting a blank page if necessary.

	This directive has no effect with non-LaTeX builders.

	.. versionadded:: 2.10.0
	.. seealso:: :rst:dir:`latex:clearpage`


.. rst:directive:: .. latex:vspace:: space

	Configures LaTeX to add or remove vertical space.

	The value for ``space`` is passed verbatim to the ``\vspace{}`` command.
	Ensure you pass a valid value.

	This directive has no effect with non-LaTeX builders.

	.. versionadded:: 2.11.0


.. raw:: latex

	\end{multicols}


API Reference
----------------
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
import re
from textwrap import dedent
from typing import Optional, cast

# 3rd party
from docutils import nodes
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import DelimitedList
from sphinx.application import Sphinx
from sphinx.builders.latex import LaTeXBuilder
from sphinx.config import Config
from sphinx.domains import Domain
from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective
from sphinx.writers.latex import LaTeXTranslator

_ = BuildEnvironment

__all__ = [
		"use_package",
		"visit_footnote",
		"depart_footnote",
		"SamepageDirective",
		"ClearPageDirective",
		"ClearDoublePageDirective",
		"VSpaceDirective",
		"LaTeXDomain",
		"replace_unknown_unicode",
		"better_header_layout",
		"configure",
		"setup",
		]

footmisc_symbols = ['0', '*', '†', '‡', '§', '¶', '‖', "**", "††", "‡‡"]


def visit_footnote(translator: LaTeXTranslator, node: nodes.footnote) -> None:
	"""
	Visit a :class:`docutils.nodes.footnote` node with the LaTeX translator.

	Unlike the default ``visit_footnote`` function, this one handles footnotes using symbols.

	.. versionadded:: 2.8.0

	:param translator:
	:param node:

	.. clearpage::
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


class SamepageDirective(SphinxDirective):
	"""
	Directive which configures LaTeX to make all content within this directive appear on the same page.

	This can be useful to avoid awkward page breaks.

	This directive has no effect with non-LaTeX builders.

	.. versionadded:: 2.9.0
	"""

	has_content = True

	def run(self):
		"""
		Process the content of the directive.
		"""

		content_node = nodes.container(rawsource='\n'.join(self.content))
		self.state.nested_parse(self.content, self.content_offset, content_node)

		return [
				nodes.raw('', r"\par\begin{samepage}", format="latex"),
				content_node,
				nodes.raw('', r"\end{samepage}\par", format="latex"),
				]


class ClearPageDirective(SphinxDirective):
	"""
	Directive which configures LaTeX to start a new page.

	This directive has no effect with non-LaTeX builders.

	.. versionadded:: 2.10.0
	.. seealso:: :class:`~.ClearDoublePageDirective`
	"""

	has_content = True

	def run(self):
		"""
		Process the content of the directive.
		"""

		return [nodes.raw('', r"\clearpage", format="latex")]


class ClearDoublePageDirective(SphinxDirective):
	"""
	Directive which configures LaTeX to start a new page.

	In a two-sided printing it also makes the next page a right-hand (odd-numbered) page,
	inserting a blank page if necessary.

	This directive has no effect with non-LaTeX builders.

	.. versionadded:: 2.10.0
	.. seealso:: :class:`~.ClearPageDirective`
	"""

	has_content = True

	def run(self):
		"""
		Process the content of the directive.
		"""

		return [nodes.raw('', r"\cleardoublepage", format="latex")]


class VSpaceDirective(SphinxDirective):
	"""
	Directive which configures LaTeX to add or remove vertical space.

	This directive has no effect with non-LaTeX builders.

	.. versionadded:: 2.11.0

	.. clearpage::
	"""

	required_arguments = 1  # the space

	def run(self):
		"""
		Process the content of the directive.
		"""

		return [nodes.raw('', fr"\vspace{{{self.arguments[0]}}}", format="latex")]


class LaTeXDomain(Domain):
	"""
	Domain containing various LaTeX-specific directives.

	.. versionadded:: 2.11.0
	"""

	name = "latex"
	label = "LaTeX"
	directives = {
			"samepage": SamepageDirective,
			"clearpage": ClearPageDirective,
			"cleardoublepage": ClearDoublePageDirective,
			"vspace": VSpaceDirective,
			}


def replace_unknown_unicode(app: Sphinx, exception: Optional[Exception] = None):
	r"""
	Replaces certain unknown unicode characters in the Sphinx LaTeX output with the best equivalents.

	.. only:: html

		The mapping is as follows:

		* ♠ -- \spadesuit
		* ♥ -- \heartsuit
		* ♦ -- \diamondsuit
		* ♣ -- \clubsuit
		* Zero width space -- \hspace{0pt}
		* μ -- \textmu
		* ≡ -- \equiv (new in version 2.11.0)

	This function can be hooked into the :event:`build-finished` event as follows:

	.. code-block:: python

		app.connect("build-finished", replace_unknown_unicode)

	.. versionadded:: 2.9.0

	:param app: The Sphinx application.
	:param exception: Any exception which occurred and caused Sphinx to abort.
	"""

	if exception:  # pragma: no cover
		return

	if app.builder.name.lower() != "latex":
		return

	builder = cast(LaTeXBuilder, app.builder)
	output_file = PathPlus(builder.outdir) / f"{builder.titles[0][1].lower()}.tex"

	output_content = output_file.read_text()

	output_content = output_content.replace('♠', r' $\spadesuit$ ')
	output_content = output_content.replace('♥', r' $\heartsuit$ ')
	output_content = output_content.replace('♦', r' $\diamondsuit$ ')
	output_content = output_content.replace('♣', r' $\clubsuit$ ')
	output_content = output_content.replace('\u200b', r'\hspace{0pt}')  # Zero width space
	output_content = output_content.replace('μ', r"\textmu")
	output_content = output_content.replace('≡', r" $\equiv$ ")

	output_file.write_clean(output_content)


def better_header_layout(
		config: Config,
		space_before: int = 10,
		space_after: int = 20,
		) -> None:
	"""
	Makes LaTeX chapter names lowercase, and adjusts the spacing above and below the chapter name.

	.. versionadded:: 2.10.0

	:param config: The Sphinx configuration object.
	:param space_before: The space, in pixels, before the chapter name.
	:param space_after: The space, in pixels, after the chapter name.
	"""

	begin = "% begin st better header layout"
	end = "% end st better header layout"

	commands = rf"""
	{begin}
	\makeatletter
		\renewcommand{{\DOCH}}{{%
			\mghrulefill{{\RW}}\par\nobreak
			\CNV\FmN{{\@chapapp}}\par\nobreak
			\CNoV\TheAlphaChapter\par\nobreak
			\vskip -1\baselineskip\vskip 5pt\mghrulefill{{\RW}}\par\nobreak
			\vskip 10\p@
			}}
		\renewcommand{{\DOTI}}[1]{{%
			\CTV\FmTi{{#1}}\par\nobreak
			\vskip {space_before}\p@
			}}
		\renewcommand{{\DOTIS}}[1]{{%
			\CTV\FmTi{{#1}}\par\nobreak
			\vskip {space_after}\p@
			}}
	\makeatother
	{end}
	"""

	if not hasattr(config, "latex_elements") or not config.latex_elements:  # pragma: no cover
		config.latex_elements = {}  # type: ignore

	latex_preamble = config.latex_elements.get("preamble", '')

	if begin in latex_preamble:
		config.latex_elements["preamble"] = re.sub(
				f"{begin}.*{end}",
				dedent(commands),
				latex_preamble,
				count=1,
				flags=re.DOTALL,
				)
	else:
		config.latex_elements["preamble"] = f"{latex_preamble}\n{dedent(commands)}"

	config.latex_elements["fncychap"] = "\\usepackage[Bjarne]{fncychap}\n\\ChNameAsIs\n\\ChTitleAsIs\n"


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

	app.add_directive("samepage", SamepageDirective)
	app.add_directive("clearpage", ClearPageDirective)
	app.add_directive("cleardoublepage", ClearDoublePageDirective)

	app.add_domain(LaTeXDomain)

	app.connect("config-inited", configure)

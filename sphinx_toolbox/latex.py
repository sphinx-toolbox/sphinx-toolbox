#!/usr/bin/env python3
#
#  latex.py
r"""
Sphinx utilities for LaTeX builders.

.. versionadded:: 2.8.0

In addition to the developer API (see below), :mod:`sphinx_toolbox.latex`
configures Sphinx and LaTeX to correctly handle symbol footnotes.

.. versionchanged:: 2.12.0

	Sphinx is also configured to respect ``.. only:: html`` etc. directives surrounding
	toctree directives when determining the overall toctree depth.

.. extensions:: sphinx_toolbox.latex


Example Footnotes
--------------------

| Hello [1]_
| Goodbye [2]_
| Symbol [*]_
| Another Symbol [*]_
| Number Again [3]_
| Symbol 3 [*]_
| Symbol 4 [*]_
| Symbol 5 [*]_
| Symbol 6 [*]_
| Symbol 7 [*]_
| Symbol 8 [*]_
| Symbol 9 [*]_

.. latex:vspace:: 20px

.. [1] One
.. [2] Two
.. [*] Buckle my shoe
.. [*] The second symbol
.. [3] The number after the symbol
.. [*] Symbol 3
.. [*] Symbol 4
.. [*] Symbol 5
.. [*] Symbol 6
.. [*] Symbol 7
.. [*] Symbol 8
.. [*] Symbol 9


.. latex:vspace:: -10px

Usage
-------

.. latex:vspace:: -20px

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

.. raw:: latex

	\columnbreak

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


.. latex:vspace:: -20px

API Reference
----------------

.. latex:vspace:: -20px
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
#  PatchedLaTeXBuilder based on Sphinx
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
import os
import re
from textwrap import dedent
from typing import Any, Optional, cast

# 3rd party
import sphinx
from docutils import nodes
from docutils.frontend import OptionParser
from docutils.transforms.references import Footnotes
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import DelimitedList
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.builders.latex import LaTeXBuilder
from sphinx.config import Config
from sphinx.domains import Domain
from sphinx.environment import BuildEnvironment
from sphinx.locale import __
from sphinx.util import progress_message
from sphinx.util.docutils import SphinxDirective, SphinxFileOutput
from sphinx.util.nodes import process_only_nodes
from sphinx.writers.latex import LaTeXTranslator, LaTeXWriter

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

footmisc_symbols = ['0', *Footnotes.symbols]
# footmisc_symbols = ['0', '*', '†', '‡', '§', '¶', '‖', "**", "††", "‡‡"]


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

	if not translator.in_parsed_literal:
		translator.body.append("%\n")

	if not footnote_id.isnumeric() and footnote_id in footmisc_symbols:
		footnote_id = str(footmisc_symbols.index(footnote_id))
		translator.body.append(r"\renewcommand\thefootnote{\thesymbolfootnote}")

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
	translator.body.append(r"\renewcommand\thefootnote{\thenumberfootnote}")
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
	"""

	required_arguments = 1  # the space

	def run(self):
		"""
		Process the content of the directive.
		"""

		return [nodes.raw('', f"\n\\vspace{{{self.arguments[0]}}}\n", format="latex")]


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
		* ≈ -- \approx (new in version 2.12.0)
		* ≥ -- \geq (new in version 2.13.0)
		* ≤ -- \leq (new in version 2.13.0)

	This function can be hooked into the :event:`build-finished` event as follows:

	.. code-block:: python

		app.connect("build-finished", replace_unknown_unicode)

	.. versionadded:: 2.9.0

	:param app: The Sphinx application.
	:param exception: Any exception which occurred and caused Sphinx to abort.
	"""

	if exception:  # pragma: no cover
		return

	if app.builder is None or app.builder.name.lower() != "latex":
		return

	builder = cast(LaTeXBuilder, app.builder)
	output_file = PathPlus(builder.outdir) / f"{builder.titles[0][1].lower()}.tex"

	output_content = output_file.read_text()

	output_content = output_content.replace('♠', r' $\spadesuit$ ')
	output_content = output_content.replace('♥', r' $\heartsuit$ ')
	output_content = output_content.replace('♦', r' $\diamondsuit$ ')
	output_content = output_content.replace('♣', r' $\clubsuit$ ')
	output_content = output_content.replace('\u200b', r'\hspace{0pt}')  # Zero width space
	output_content = output_content.replace('μ', r"\textmu{}")
	output_content = output_content.replace('≡', r" $\equiv$ ")
	output_content = output_content.replace('≈', r" $\approx$ ")
	output_content = output_content.replace('≥', r" $\geq$ ")
	output_content = output_content.replace('≤', r" $\leq$ ")

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


class PatchedLaTeXBuilder(LaTeXBuilder):
	"""
	Patched version of Sphinx's LaTeX builder which skips toctrees under ``.. only:: html`` etc. directives
	when determining the max toctree depth.

	The default behaviour uses the ``:maxdepth:`` option of the first toctree,
	irrespective of whether the toctree will exist with the LaTeX builder.
	"""  # noqa: D400

	# TODO: respect toctree caption for LaTeX table of contents too
	# \addto\captionsenglish{\renewcommand{\contentsname}{Documentation}}

	def write(self, *ignored: Any) -> None:
		assert self.env is not None

		docwriter = LaTeXWriter(self)
		docsettings: Any = OptionParser(
				defaults=self.env.settings,
				components=(docwriter, ),
				read_config_files=True,
				).get_default_values()

		if sphinx.version_info <= (4, 0):
			# 3rd party
			from sphinx.builders.latex import patch_settings  # type: ignore
			patch_settings(docsettings)

		self.init_document_data()
		self.write_stylesheet()

		for entry in self.document_data:
			docname, targetname, title, author, themename = entry[:5]
			theme = self.themes.get(themename)
			toctree_only = False
			if len(entry) > 5:
				toctree_only = entry[5]
			destination = SphinxFileOutput(
					destination_path=os.path.join(self.outdir, targetname),
					encoding="utf-8",
					overwrite_if_changed=True
					)
			with progress_message(__("processing %s") % targetname):
				doctree = self.env.get_doctree(docname)
				process_only_nodes(doctree, self.tags)
				toctree = next(iter(doctree.traverse(addnodes.toctree)), None)
				if toctree and toctree.get("maxdepth") > 0:
					tocdepth = toctree.get("maxdepth")
				else:
					tocdepth = None

				doctree = self.assemble_doctree(
						docname,
						toctree_only,
						appendices=(self.config.latex_appendices if theme.name != "howto" else [])
						)
				doctree["docclass"] = theme.docclass
				doctree["contentsname"] = self.get_contentsname(docname)
				doctree["tocdepth"] = tocdepth
				self.post_process_images(doctree)
				self.update_doc_context(title, author, theme)

				if hasattr(self, "update_context"):  # pragma: no cover
					# Only present in newer Sphinx versions
					self.update_context()

			with progress_message(__("writing")):
				docsettings._author = author
				docsettings._title = title
				docsettings._contentsname = doctree["contentsname"]
				docsettings._docname = docname
				docsettings._docclass = theme.name

				doctree.settings = docsettings
				docwriter.theme = theme
				docwriter.write(doctree, destination)


def configure(app: Sphinx, config: Config):
	"""
	Configure :mod:`sphinx_toolbox.latex`.

	:param app: The Sphinx application.
	:param config:
	"""

	if not hasattr(config, "latex_elements") or not config.latex_elements:  # pragma: no cover
		config.latex_elements = {}  # type: ignore

	latex_preamble = config.latex_elements.get("preamble", '')

	command_string = r"\newcommand\thesymbolfootnote{\fnsymbol{footnote}}\let\thenumberfootnote\thefootnote"

	if command_string not in latex_preamble:
		config.latex_elements["preamble"] = f"{latex_preamble}\n{command_string}"


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

	app.add_builder(PatchedLaTeXBuilder, override=True)

	app.connect("config-inited", configure)

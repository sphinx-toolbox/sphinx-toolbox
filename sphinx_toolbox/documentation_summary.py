#!/usr/bin/env python3
#
#  documentation_summary.py
"""
Allows insertion of a summary line on the title page generated with the LaTeX builder,
and at a custom location throughout the document.

.. versionadded:: 2.2.0
.. extensions:: sphinx_toolbox.documentation_summary


Configuration
--------------

.. confval:: documentation_summary
	:type: :class:`str`

	The documentation summary to display on the title page with the LaTeX builder,
	and at the location of :rst:dir:`documentation-summary` directives for other builders.

	If undefined no summary is shown.


Usage
------

.. rst:directive:: documentation-summary

	Adds the documentation summary as configured above.

	**Example**

	.. rest-example::

		.. documentation-summary::


	.. rst:directive:option:: meta

		Include the summary as a meta_ "description" tag in the HTML output.

		The structure of the description is ``{project} -- {summary}``,
		where ``project`` is configured in ``conf.py``.

		See `the sphinx documentation`_ for more information on the ``project`` option.

		.. versionadded:: 2.10.0

		.. _meta: https://developer.mozilla.org/en-US/docs/Web/HTML/Element/meta
		.. _the sphinx documentation: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-project

API Reference
----------------

"""  # noqa: D400
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
from typing import List

# 3rd party
from docutils import nodes
from docutils.statemachine import StringList
from docutils.utils.smartquotes import educateQuotes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util.docutils import SphinxDirective

# this package
from sphinx_toolbox.utils import Purger, SphinxExtMetadata, flag, metadata_add_version

__all__ = ["DocumentationSummaryDirective", "configure", "setup"]

summary_node_purger = Purger("all_summary_nodes")

RENEW = r"""
\makeatletter
\renewcommand{\py@release}{
	\releasename\space\version
	\par
	\vspace{25pt}
	\textup{\thesummary}
}
\makeatother
"""

RESET = r"\makeatletter\renewcommand{\py@release}{\releasename\space\version}\makeatother"


class DocumentationSummaryDirective(SphinxDirective):
	"""
	A Sphinx directive for creating a summary line.
	"""

	option_spec = {"meta": flag}

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the directive.
		"""

		summary = getattr(self.config, "documentation_summary", '').strip()

		if not summary:
			return []  # pragma: no cover

		# if self.env.app.builder.format.lower() == "latex" or not summary:
		# 	return []

		targetid = f'documentation-summary-{self.env.new_serialno("documentation-summary"):d}'

		onlynode = addnodes.only(expr="html")

		content = f'**{summary}**'
		content_node = nodes.paragraph(rawsource=content, ids=[targetid])
		onlynode += content_node
		self.state.nested_parse(StringList([content]), self.content_offset, content_node)
		summary_node_purger.add_node(self.env, content_node, content_node, self.lineno)

		if "meta" in self.options:
			meta_content = f'.. meta::\n    :description: {self.config.project} -- {summary}\n'
			meta_node = nodes.paragraph(rawsource=meta_content, ids=[targetid])
			onlynode += meta_node
			self.state.nested_parse(
					StringList(meta_content.split('\n')),
					self.content_offset,
					meta_node,
					)
			summary_node_purger.add_node(self.env, meta_node, meta_node, self.lineno)

		return [onlynode]


def configure(app: Sphinx, config: Config):
	"""
	Configure :mod:`sphinx_toolbox.documentation_summary`.

	:param app: The Sphinx application.
	:param config:
	"""

	if not hasattr(config, "latex_elements"):  # pragma: no cover
		config.latex_elements = {}  # type: ignore

	latex_elements = (config.latex_elements or {})

	latex_preamble = latex_elements.get("preamble", '')
	summary = getattr(config, "documentation_summary", '').strip()

	if not summary:
		return  # pragma: no cover

	# Escape latex special characters
	summary = summary.replace("~ ", r"\textasciitilde\space ")
	summary = summary.replace("^ ", r"\textasciicircum\space ")
	summary = summary.replace("\\ ", r"\textbackslash\space ")

	summary = summary.translate({
			35: r"\#",
			36: r"\$",
			37: r"\%",
			38: r"\&",
			94: r"\textasciicircum",
			95: r"\_",
			123: r"\{",
			125: r"\}",
			126: r"\textasciitilde",
			})

	# TODO: escape backslashes without breaking the LaTeX commands

	summary_command = rf"\newcommand{{\thesummary}}{{{educateQuotes(summary)}}}"

	if summary_command not in latex_preamble:
		config.latex_elements["preamble"] = '\n'.join([
				latex_preamble,
				summary_command,
				RENEW,
				])
		config.latex_elements["maketitle"] = '\n'.join([
				config.latex_elements.get("maketitle", r"\sphinxmaketitle"),
				RESET,
				])


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.documentation_summary`.

	:param app: The Sphinx application.
	"""

	app.connect("config-inited", configure, priority=550)
	app.add_directive("documentation-summary", DocumentationSummaryDirective)
	app.add_config_value("documentation_summary", None, "env", types=[str, None])
	app.connect("env-purge-doc", summary_node_purger.purge_nodes)

	return {"parallel_read_safe": True}

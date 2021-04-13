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
from docutils.statemachine import ViewList
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util.docutils import SphinxDirective

# this package
from sphinx_toolbox.utils import Purger, SphinxExtMetadata, metadata_add_version

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

	def run(self) -> List[nodes.Node]:
		"""
		Process the content of the directive.
		"""

		summary = getattr(self.config, "documentation_summary", None)

		if self.env.app.builder.format.lower() == "latex" or not summary:
			return []

		targetid = f'documentation-summary-{self.env.new_serialno("documentation-summary"):d}'

		content = f'**{summary}**'
		targetnode = nodes.paragraph(rawsource=f'**{summary}**', ids=[targetid])
		self.state.nested_parse(ViewList([content]), self.content_offset, targetnode)  # type: ignore

		summary_node_purger.add_node(self.env, targetnode, targetnode, self.lineno)

		return [targetnode]


def configure(app: Sphinx, config: Config):
	"""
	Configure :mod:`sphinx_toolbox.documentation_summary`.

	:param app:
	:param config:
	"""

	if not hasattr(config, "latex_elements"):  # pragma: no cover
		config.latex_elements = {}  # type: ignore

	latex_elements = (config.latex_elements or {})

	latex_preamble = latex_elements.get("preamble", '')
	summary = getattr(config, "documentation_summary", None)

	if not summary:
		return  # pragma: no cover

	summary_command = rf"\newcommand{{\thesummary}}{{{summary}}}"

	if summary_command not in latex_preamble:
		config.latex_elements["preamble"] = '\n'.join([
				latex_preamble,
				summary_command,
				RENEW,
				])
		config.latex_elements["maketitle"] = '\n'.join([r"\sphinxmaketitle", RESET])


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.documentation_summary`.

	:param app:
	"""

	app.connect("config-inited", configure)
	app.add_directive("documentation-summary", DocumentationSummaryDirective)
	app.add_config_value("documentation_summary", None, "env", types=[str, None])
	app.connect("env-purge-doc", summary_node_purger.purge_nodes)

	return {"parallel_read_safe": True}

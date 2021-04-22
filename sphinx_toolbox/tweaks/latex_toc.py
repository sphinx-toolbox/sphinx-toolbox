#!/usr/bin/env python3
#
#  latex_toc.py
"""
Adjusts the default LaTeX output as follows:

* The captions from ``toctree`` directives are converted into document parts.
* The PDF outline has the correct hierarchy, including having the indices as top-level elements.

.. versionadded:: 2.1.0

.. extensions:: sphinx_toolbox.tweaks.latex_toc

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
import sphinx.directives.other
import sphinx.writers.latex
from docutils import nodes
from sphinx.application import Sphinx
from sphinx.config import Config

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["setup", "configure"]

use_bookmark = r"\usepackage{bookmark}"
nest_bookmark_level_part = "\\bookmarksetupnext{{level=part}}\n"


class LaTeXTranslator(sphinx.writers.latex.LaTeXTranslator):

	def generate_indices(self) -> str:

		super_output = super().generate_indices()

		if not super_output:
			return nest_bookmark_level_part

		return '\n'.join([
				nest_bookmark_level_part,
				*super_output.splitlines(),
				'',
				nest_bookmark_level_part,
				])


class LatexTocTreeDirective(sphinx.directives.other.TocTree):

	def run(self) -> List[nodes.Node]:

		output: List[nodes.Node] = []
		caption = self.options.get("caption")

		if (
				caption is not None and self.env.app.builder.format.lower() == "latex"
				and self.env.docname == self.env.config.master_doc
				):

			latex_part_node = nodes.raw(text=f"\\chapter{{{caption}}}", format="latex")

			output.append(latex_part_node)

		output.extend(super().run())

		return output


def configure(app: Sphinx, config: Config):
	"""
	Configure :mod:`sphinx_toolbox.tweaks.latex_toc`.

	:param app:
	:param config:
	"""

	if not hasattr(config, "latex_elements"):
		config.latex_elements = {}  # type: ignore

	latex_preamble = (config.latex_elements or {}).get("preamble", '')

	if use_bookmark not in latex_preamble:
		config.latex_elements["preamble"] = f"{latex_preamble}\n{use_bookmark}"


def purge_outdated(app: Sphinx, env, added, changed, removed):
	return [env.config.master_doc]


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.tweaks.latex_toc`.

	:param app:
	"""

	app.connect("env-get-outdated", purge_outdated)
	app.connect("config-inited", configure)
	app.add_directive("toctree", LatexTocTreeDirective, override=True)
	app.set_translator("latex", LaTeXTranslator, override=True)

	return {"parallel_read_safe": True}

#!/usr/bin/env python3
#
#  sidebar_links.py
r"""
Directive which adds a toctree to the sidebar containing links to the GitHub repository, PyPI project page etc.

.. versionadded:: 2.9.0

.. extensions:: sphinx_toolbox.sidebar_links


.. latex:vspace:: -5px

Usage
-------

.. latex:vspace:: -10px

.. rst:directive:: sidebar-links

	Adds a toctree to the sidebar containing links to the GitHub repository, PyPI project page etc.
	The toctree is only shown in the sidebar and is hidden with non-HTML builders.

	.. only:: html

		You can see an example of this in the sidebar of this documentation.

	.. note:: This directive can only be used on the root document (i.e. index.rst).

	.. rst:directive:option:: github
		:type: flag

		Flag to add a link to the project's GitHub repository.

		To use this option add the following to your ``conf.py``:

		.. code-block:: python

			extensions = [
					...
					'sphinx_toolbox.github',
					]

			github_username = '<your username>'
			github_repository = '<your repository>'


		See :mod:`sphinx_toolbox.github` for more information.

	.. rst:directive:option:: pypi
		:type: string

		Flag to add a link to the project page on PyPI.

		The name of the project on PyPI must be passed as the option's value.

	.. rst:directive:option:: caption
		:type: string

		The caption of the toctree. Defaults to ``Links``

	Additional toctree entries may be added as the content of the directive, in the same manner as normal toctrees.


API Reference
--------------
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
import warnings
from typing import List

# 3rd party
import docutils
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from domdf_python_tools.stringlist import StringList
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

# this package
from sphinx_toolbox.utils import OptionSpec, SphinxExtMetadata, flag, metadata_add_version

__all__ = ["SidebarLinksDirective", "setup"]


class SidebarLinksDirective(SphinxDirective):
	"""
	Directive which adds a toctree to the sidebar containing links to the GitHub repository, PyPI project page etc.
	"""

	has_content: bool = True

	option_spec: OptionSpec = {  # type: ignore
		"pypi": directives.unchanged_required,
		"github": flag,
		"caption": directives.unchanged_required,
		}

	def process_github_option(self) -> str:
		"""
		Process the ``:github:`` flag.
		"""

		if "sphinx_toolbox.github" not in self.env.app.extensions:
			raise ValueError(
					"The 'sphinx_toolbox.github' extension is required for the "
					":github: option but it is not enabled!"
					)

		username = getattr(self.env.config, "github_username", None)
		if username is None:
			raise ValueError("'github_username' has not been set in 'conf.py'!")

		repository = getattr(self.env.config, "github_repository", None)
		if repository is None:
			raise ValueError("'github_repository' has not been set in 'conf.py'!")

		return f"GitHub <https://github.com/{username}/{repository}>"

	def run(self) -> List[nodes.Node]:
		"""
		Create the installation node.
		"""

		if self.env.docname != self.env.config.master_doc:  # pragma: no cover
			warnings.warn(
					"The 'sidebar-links' directive can only be used on the Sphinx master doc. "
					"No links will be shown.",
					UserWarning,
					)
			return []

		body = StringList([
				".. toctree::",
				"    :hidden:",
				])

		with body.with_indent("    ", 1):
			if "caption" in self.options:
				body.append(f":caption: {self.options['caption']}")
			else:  # pragma: no cover
				body.append(":caption: Links")

			body.blankline()

			if "github" in self.options:
				body.append(self.process_github_option())
			if "pypi" in self.options:
				body.append(f"PyPI <https://pypi.org/project/{self.options['pypi']}>")

			body.extend(self.content)

		body.blankline()
		body.blankline()

		only_node = addnodes.only(expr="html")
		content_node = nodes.paragraph(rawsource=str(body))
		only_node += content_node
		self.state.nested_parse(docutils.statemachine.StringList(body), self.content_offset, content_node)

		return [only_node]


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.sidebar_links`.

	:param app: The Sphinx application.
	"""

	app.add_directive("sidebar-links", SidebarLinksDirective)

	return {"parallel_read_safe": True}

#!/usr/bin/env python3
#
#  tabsize.py
r"""
Hack to get the docutils tab size, as there doesn't appear to be any other way.

.. versionadded:: 1.0.0


API Reference
---------------

You probably don't need to use this extension directly, but if you're developing an
extension of your own you can enable it like so:

.. code-block::

	def setup(app: Sphinx) -> Dict[str, Any]:
		app.setup_extension('sphinx_toolbox.github')
		return {}

This will guarantee that the following value will be available via
:attr:`app.config <sphinx.config.Config>`:

* **docutils_tab_width** (:class:`int`\) -- The number of spaces that correspond to a tab when Docutils parses source files.

"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from typing import Union

# 3rd party
from docutils.nodes import document
from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.parsers import RSTParser

# this package
from sphinx_toolbox.utils import SphinxExtMetadata

__all__ = ["setup"]


def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.tweaks.tabsize`.

	:param app: The Sphinx app.

	.. versionadded:: 1.0.0
	"""

	# this package
	from sphinx_toolbox import __version__

	class CustomRSTParser(RSTParser):

		def parse(self, inputstring: Union[str, StringList], document: document) -> None:
			app.config.docutils_tab_width = document.settings.tab_width  # type: ignore
			super().parse(inputstring, document)

	app.add_source_parser(CustomRSTParser, override=True)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

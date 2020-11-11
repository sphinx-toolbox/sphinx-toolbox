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

	.. rst:directive:option:: tab-width:
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


API Reference
----------------

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
from typing import List

# 3rd party
from docutils.nodes import Node
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from domdf_python_tools.utils import convert_indents
from sphinx.application import Sphinx
from sphinx.directives.code import CodeBlock as __BaseCodeBlock

# this package
from sphinx_toolbox.utils import OptionSpec, SphinxExtMetadata

__all__ = ["CodeBlock", "setup"]


class CodeBlock(__BaseCodeBlock):
	"""
	Directive for a code block with special highlighting or line numbering settings.

	The indent_size can be adjusted with the ``:tab-width: <int>`` option.
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

		self.content = StringList(code.split('\n'))

		return super().run()


def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.code`.

	:param app: The Sphinx app.

	.. versionadded:: 1.0.0
	"""

	# this package
	from sphinx_toolbox import __version__

	# Code block with customisable indent size.
	app.add_directive("code-block", CodeBlock, override=True)
	app.add_directive("sourcecode", CodeBlock, override=True)

	# Hack to get the docutils tab size, as there doesn't appear to be any other way
	app.setup_extension("sphinx_toolbox.tweaks.tabsize")

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

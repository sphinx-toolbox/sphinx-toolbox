#!/usr/bin/env python3
#
#  rest_example.py
"""
The :rst:dir:`rest-example` directive.
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
from typing import Any, Callable, Dict, List, Mapping, Sequence

# 3rd party
import sphinx.environment
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx.util.docutils import SphinxDirective

# this package
from sphinx_toolbox.utils import OptionSpec, Purger

__all__ = ["reSTExampleDirective", "make_rest_example", "rest_example_purger"]


class reSTExampleDirective(SphinxDirective):
	"""
	Directive to show some restructured text source, and the rendered output.
	"""

	has_content: bool = True

	# Options to pass through to .. code-block::
	option_spec: OptionSpec = {  # type: ignore
		"force": directives.flag,
		"emphasize-lines": directives.unchanged,
		"tab-width": int,
		"dedent": int,
		}

	def run(self) -> List[nodes.Node]:
		"""
		Create the rest_example node.

		:return:
		"""

		targetid = f'example-{self.env.new_serialno("sphinx-toolbox rest_example"):d}'
		targetnode = nodes.target('', '', ids=[targetid])

		content = make_rest_example(
				self.options,
				self.env,
				self.content,  # type: ignore
				)
		view = ViewList(content)

		example_node = nodes.paragraph(rawsource=content)  # type: ignore
		self.state.nested_parse(view, self.content_offset, example_node)  # type: ignore

		rest_example_purger.add_node(self.env, example_node, targetnode, self.lineno)

		return [targetnode, example_node]


def make_rest_example(
		options: Dict[str, Any],
		env: sphinx.environment.BuildEnvironment,
		content: Sequence[str],
		) -> List[str]:
	"""
	Make the content of a reST Example node.

	:param options:
	:param content: The user-provided content of the directive.

	:return:
	"""

	output = [".. code-block:: rest"]
	tab = ' ' * env.config.docutils_tab_width

	for option, value in options.items():
		if value is None:
			output.append(f"{tab}:{option}:")
		else:
			output.append(f"{tab}:{option}: {value}")

	output.append('')

	for line in content:
		output.append(f"{tab}{line}")

	if output[-1]:
		output.append('')

	for line in content:
		output.append(line)

	if output[-1]:
		output.append('')

	return output


rest_example_purger = Purger("all_rest_example_nodes")

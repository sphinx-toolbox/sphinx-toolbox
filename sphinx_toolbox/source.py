#!/usr/bin/env python3
#
#  source.py
"""
Add hyperlinks to source files, either on GitHub or in the documentation itself.

If you're looking for a ``[source]`` button to go at the end of your class and
function signatures, checkout
`sphinx.ext.linkcode <https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html>`__
and
`sphinx.ext.viewcode <https://www.sphinx-doc.org/en/master/usage/extensions/viewcode.html>`__
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
#  Based on pyspecific.py from the Python documentation.
#  Copyright 2008-2014 by Georg Brandl.
#  Licensed under the PSF License 2.0
#
#  Parts of the docstrings based on https://docutils.sourceforge.io/docs/howto/rst-roles.html
#

# stdlib
from typing import Dict, List, Sequence, Tuple, Union

# 3rd party
from docutils import nodes, utils
from docutils.nodes import system_message
from docutils.parsers.rst.states import Inliner
from sphinx import addnodes
from sphinx.util import split_explicit_title

__all__ = ["source_role"]

# TODO: rawstring: Return it as a problematic node linked to a system message if a problem is encountered.


def source_role(
		name: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict = {},
		content: List[str] = []
		) -> Tuple[Sequence[Union[nodes.reference, addnodes.only]], List[system_message]]:
	"""
	Adds a link to the given Python source file in the documentation or on GitHub.

	:param name: The local name of the interpreted role, the role name actually used in the document.
	:param rawtext: A string containing the entire interpreted text input, including the role and markup.
	:param text: The interpreted text content.
	:param lineno: The line number where the interpreted text begins.
	:param inliner: The :class:`docutils.parsers.rst.states.Inliner` object that called :func:`~.source_role`.
		It contains the several attributes useful for error reporting and document tree access.
	:param options: A dictionary of directive options for customization (from the ``role`` directive),
		to be interpreted by the function.
		Used for additional attributes for the generated elements and other functionality.
	:param content: A list of strings, the directive content for customization (from the ``role`` directive).
		To be interpreted by the function.

	:return: A list containing the created node, and a list containing any messages generated during the function.
	"""

	has_t, title, target = split_explicit_title(text)
	title = utils.unescape(title)
	target = utils.unescape(target)

	env = inliner.document.settings.env
	config = env.app.config

	nodes_: List[Union[nodes.reference, addnodes.only]] = []
	messages: List[system_message] = []
	refnode: Union[nodes.reference, addnodes.only]

	if config.source_link_target == "sphinx":
		pagename = "_modules/" + target.replace(".py", '')
		refnode = addnodes.only(expr="html")
		refnode += addnodes.pending_xref(
				title,
				nodes.inline(title, title),
				reftype="viewcode",
				refdomain="std",
				refexplicit=False,
				reftarget=pagename,
				refid=title,
				refdoc=env.docname,
				)

		nodes_.append(refnode)

	elif config.source_link_target == "github":
		refnode = nodes.reference(
				title,
				title,
				refuri=str(config.github_source_url / target),
				)

		nodes_.append(refnode)

	else:
		message = inliner.document.reporter.error(f"Unsupported source link target '{config.source_link_target}'.")
		messages.append(message)

	return nodes_, messages

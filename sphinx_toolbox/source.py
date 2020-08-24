#!/usr/bin/env python3
#
#  source.py
"""
Add hyperlinks to source files, either on GitHub or in the documentation itself.

If you're looking for a ``[SOURCE]`` button to go at the end of your class and
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

# stdlib
from typing import Dict, List, Tuple

# 3rd party
from docutils import nodes, utils
from docutils.nodes import Node, system_message
from docutils.parsers.rst.states import Inliner
from sphinx import addnodes
from sphinx.util import split_explicit_title

__all__ = ["source_role"]


def source_role(
		typ: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict = {},
		content: List[str] = []
		) -> Tuple[List[Node], List[system_message]]:
	"""
	Adds a link to the given Python source file in the documentation or on GitHub.

	:param typ:
	:param rawtext:
	:param text:
	:param lineno:
	:param inliner:
	:param options:
	:param content:

	:return:
	"""

	has_t, title, target = split_explicit_title(text)
	title = utils.unescape(title)
	target = utils.unescape(target)

	env = inliner.document.settings.env
	config = env.app.config
	if config.source_link_target == "sphinx":
		pagename = '_modules/' + target.replace('.py', '')
		refnode = addnodes.only(expr='html')
		refnode += addnodes.pending_xref(
				title,
				nodes.paragraph(title, title),
				reftype='viewcode',
				refdomain='std',
				refexplicit=False,
				reftarget=pagename,
				refid=title,
				refdoc=env.docname,
				)
	elif config.source_link_target == "github":
		refnode = nodes.reference(
				title,
				title,
				refuri=str(config.github_source_url / target),
				)
	else:
		raise NotImplementedError(f"Unsupported source link target '{config.source_link_target}'.")

	return [refnode], []

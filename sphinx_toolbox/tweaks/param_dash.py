#!/usr/bin/env python3
#
#  param_dash.py
"""
Monkeypatches :class:`sphinx.util.docfields.TypedField`
to only output the endash (--) separating the parameter
name from its description if a description was given.

.. versionadded:: 0.9.0


**Example:**

.. rest-example::

	.. class:: MyClass(foo, bar)

		This is my class.

		:param foo: An argument
		:param bar:


.. extensions:: sphinx_toolbox.tweaks.param_dash

"""  # noqa D400
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
#  Parts based on https://github.com/sphinx-doc/sphinx
#  |  Copyright (c) 2007-2020 by the Sphinx team (see AUTHORS file).
#  |  BSD Licensed
#  |  All rights reserved.
#  |
#  |  Redistribution and use in source and binary forms, with or without
#  |  modification, are permitted provided that the following conditions are
#  |  met:
#  |
#  |  * Redistributions of source code must retain the above copyright
#  |   notice, this list of conditions and the following disclaimer.
#  |
#  |  * Redistributions in binary form must reproduce the above copyright
#  |   notice, this list of conditions and the following disclaimer in the
#  |   documentation and/or other materials provided with the distribution.
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
from typing import Dict, List, Tuple

# 3rd party
import sphinx.util.docfields
from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["make_field", "setup"]


def make_field(  # noqa D102
		self,
		types: Dict[str, List[nodes.Node]],
		domain: str,
		items: Tuple,
		env: BuildEnvironment = None,
		) -> nodes.field:

	def handle_item(fieldarg: str, content: List[nodes.Element]) -> nodes.paragraph:
		par = nodes.paragraph()
		par.extend(self.make_xrefs(self.rolename, domain, fieldarg, addnodes.literal_strong, env=env))

		if fieldarg in types:
			par += nodes.Text(" (")
			# NOTE: using .pop() here to prevent a single type node to be
			# inserted twice into the doctree, which leads to
			# inconsistencies later when references are resolved
			fieldtype = types.pop(fieldarg)

			if len(fieldtype) == 1 and isinstance(fieldtype[0], nodes.Text):
				typename = fieldtype[0].astext()
				par.extend(
						self.make_xrefs(self.typerolename, domain, typename, addnodes.literal_emphasis, env=env)
						)
			else:
				par += fieldtype

			par += nodes.Text(')')

		if (content and len(content) == 1 and isinstance(content[0], nodes.inline) and not content[0].children):
			return par

		par += nodes.Text(" -- ")
		par += content

		return par

	fieldname = nodes.field_name('', self.label)
	bodynode: nodes.Node

	if len(items) == 1 and self.can_collapse:
		fieldarg, content = items[0]
		bodynode = handle_item(fieldarg, content)
	else:
		bodynode = self.list_type()
		for fieldarg, content in items:
			bodynode += nodes.list_item('', handle_item(fieldarg, content))  # type: ignore

	fieldbody = nodes.field_body('', bodynode)

	return nodes.field('', fieldname, fieldbody)


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.tweaks.param_dash`.

	:param app: The Sphinx application.
	"""

	sphinx.util.docfields.TypedField.make_field = make_field  # type: ignore

	return {"parallel_read_safe": True}

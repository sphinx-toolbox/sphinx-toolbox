#!/usr/bin/env python3
#
#  changeset.py
"""
Customised versions of Sphinx's :rst:dir:`versionadded`, :rst:dir:`versionchanged`
and :rst:dir:`deprecated` directives to correctly handle bullet lists.

.. versionadded:: 2.11.0
.. extensions:: sphinx_toolbox.changeset

.. latex:vspace:: -10px

Usage
------

.. rst:directive:: .. versionadded:: version

   Documents the version of the project which added the described feature.

   The first argument must be given and is the version in question; you can add
   a second argument consisting of a *brief* explanation of the change.
   Alternatively, a longer description my be given in the body of the directive.

.. rst:directive:: .. versionchanged:: version

   Similar to :rst:dir:`versionadded`, but describes when and what changed in
   the feature in some way (new parameters, changed side effects, etc.).

.. rst:directive:: .. deprecated:: version

   Similar to :rst:dir:`versionchanged`, but describes when the feature was deprecated.
   An explanation can also be given, for example to inform the reader what should be used instead.


This extension also adds the following directive:

.. rst:directive:: .. versionremoved:: version [details]

   Similar to :rst:dir:`versionchanged`, but describes when the feature was or will be removed.
   An explanation can also be given, for example to inform the reader what should be used instead.


.. latex:vspace:: -10px

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
#  Based on Sphinx
#  Copyright (c) 2007-2021 by the Sphinx team.
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
from typing import List, Optional, cast

# 3rd party
import sphinx.domains.changeset
from docutils import nodes
from docutils.nodes import Node
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import _

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["VersionChange", "setup"]

versionlabels = {
		"versionremoved": _("Removed in version %s"),
		**sphinx.domains.changeset.versionlabels,
		}

versionlabel_classes = {
		"versionremoved": "removed",
		**sphinx.domains.changeset.versionlabel_classes,
		}


class VersionChange(sphinx.domains.changeset.VersionChange):
	"""
	Directive to describe a addition/change/deprecation/removal in a specific version.
	"""

	def run(self) -> List[Node]:
		"""
		Process the content of the directive.
		"""

		node = addnodes.versionmodified()
		node.document = self.state.document
		self.set_source_info(node)

		node["type"] = self.name
		node["version"] = self.arguments[0]

		text = versionlabels[self.name] % self.arguments[0]

		if len(self.arguments) == 2:
			inodes, messages = self.state.inline_text(self.arguments[1], self.lineno + 1)
			para = nodes.paragraph(self.arguments[1], '', *inodes, translatable=False)
			self.set_source_info(para)
			node.append(para)
		else:
			messages = []

		if self.content:
			self.state.nested_parse(self.content, self.content_offset, node)

		classes = ["versionmodified", versionlabel_classes[self.name]]

		if len(node):
			to_add: Optional[nodes.Node] = None

			if isinstance(node[0], nodes.paragraph) and node[0].rawsource:
				content = nodes.inline(node[0].rawsource, translatable=True)
				content.source = node[0].source
				content.line = node[0].line
				content += node[0].children
				node[0].replace_self(nodes.paragraph('', '', content, translatable=False))

			elif isinstance(node[0], (nodes.bullet_list, nodes.enumerated_list)):
				# Fix for incorrect ordering with bullet lists
				node.insert(0, nodes.compound(''))
				to_add = nodes.paragraph('', '')

			para = cast(nodes.paragraph, node[0])
			para.insert(0, nodes.inline('', f'{text}: ', classes=classes))

			if to_add is not None:
				node.insert(0, to_add)

		else:
			para = nodes.paragraph(
					'',
					'',
					nodes.inline('', f'{text}.', classes=classes),
					translatable=False,
					)
			node.append(para)

		domain = cast(
				sphinx.domains.changeset.ChangeSetDomain,
				self.env.get_domain("changeset"),
				)
		domain.note_changeset(node)

		ret = [node]  # type: List[Node]
		ret += messages
		return ret


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.changeset`.

	:param app: The Sphinx application.
	"""

	app.add_directive("deprecated", VersionChange, override=True)
	app.add_directive("versionadded", VersionChange, override=True)
	app.add_directive("versionchanged", VersionChange, override=True)
	app.add_directive("versionremoved", VersionChange, override=True)

	return {
			"parallel_read_safe": True,
			"parallel_write_safe": True,
			}

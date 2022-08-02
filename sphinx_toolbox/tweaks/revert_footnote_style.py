#!/usr/bin/env python3
#
#  revert_footnote_style.py
"""
Reverts the docutils footnote behaviour from ``>=0.18`` to that of ``<=0.17``.

.. versionadded:: 3.1.2
.. extensions:: sphinx_toolbox.tweaks.revert_footnote_style

-----

"""
#
#  Copyright © 2022 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#  Based on docutils
#  |  Copyright © 2016 David Goodger, Günter Milde
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

# 3rd party
import docutils
from sphinx.application import Sphinx
from sphinx.writers.html import HTMLTranslator
from sphinx.writers.html5 import HTML5Translator

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["setup"]


def visit_footnote(self: HTMLTranslator, node: docutils.nodes.footnote) -> None:  # pragma: no cover
	if not self.in_footnote_list:
		listnode = node.copy()
		listnode["ids"] = []
		classes = [node.tagname, self.settings.footnote_references]
		self.body.append(self.starttag(listnode, "dl", CLASS=' '.join(classes)))  # role="note"
		self.in_footnote_list = True


def depart_footnote(self, node: docutils.nodes.footnote) -> None:  # pragma: no cover
	self.body.append('</dd>\n')
	if not isinstance(node.next_node(descend=False, siblings=True), docutils.nodes.footnote):
		self.body.append('</dl>\n')
		self.in_footnote_list = False


def visit_footnote_reference(self, node: docutils.nodes.footnote_reference) -> None:  # pragma: no cover
	href = '#' + node["refid"]
	classes = ["footnote-reference", self.settings.footnote_references]
	self.body.append(self.starttag(node, 'a', suffix='', CLASS=' '.join(classes), href=href))  # role='doc-noteref'


def depart_footnote_reference(self, node: docutils.nodes.footnote_reference) -> None:  # pragma: no cover
	self.body.append("</a>")


# footnote and citation labels:
def visit_label(self, node: docutils.nodes.label) -> None:  # pragma: no cover
	if (isinstance(node.parent, docutils.nodes.footnote)):
		classes = self.settings.footnote_references
	else:
		classes = "brackets"

	# pass parent node to get id into starttag:
	self.body.append(self.starttag(node.parent, "dt", '', CLASS="label"))
	self.body.append(self.starttag(node, "span", '', CLASS=classes))

	# footnote/citation backrefs:
	if self.settings.footnote_backlinks:
		backrefs = node.parent.get("backrefs", [])
		if len(backrefs) == 1:
			self.body.append('<a class="fn-backref" href="#%s">' % backrefs[0])


def depart_label(self, node: docutils.nodes.label) -> None:  # pragma: no cover
	if self.settings.footnote_backlinks:
		backrefs = node.parent["backrefs"]
		if len(backrefs) == 1:
			self.body.append("</a>")
	self.body.append("</span>")
	if self.settings.footnote_backlinks and len(backrefs) > 1:
		backlinks = [f'<a href="#{ref}">{i}</a>' for (i, ref) in enumerate(backrefs, 1)]
		self.body.append('<span class="fn-backref">(%s)</span>' % ','.join(backlinks))
	self.body.append('</dt>\n<dd>')


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.tweaks.revert_footnote_style`.

	:param app: The Sphinx application.
	"""

	if docutils.__version_info__ >= (0, 18):  # pragma: no cover
		app.add_node(
				docutils.nodes.footnote,
				html=(visit_footnote, depart_footnote),
				override=True,
				)
		app.add_node(
				docutils.nodes.footnote_reference,
				html=(visit_footnote_reference, depart_footnote_reference),
				override=True,
				)
		app.add_node(
				docutils.nodes.label,
				html=(visit_label, depart_label),
				override=True,
				)
		HTMLTranslator.in_footnote_list = False
		HTML5Translator.in_footnote_list = False

	return {"parallel_read_safe": True}

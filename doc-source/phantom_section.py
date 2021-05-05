#!/usr/bin/env python3
#
#  __init__.py
"""
Sphinx extension to create a phantom section.
"""
# Based on https://github.com/sphinx-doc/sphinx/blob/3.x/sphinx/writers/latex.py
#
# Copyright (c) 2007-2021 by the Sphinx team.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
# * Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
from typing import List

# 3rd party
import sphinx.transforms
from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import __
from sphinx.util import logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.nodes import clean_astext
from sphinx.writers.latex import LaTeXTranslator

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2021 Dominic Davis-Foster"
__license__: str = "BSD License"
__version__: str = "0.0.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["MarkPhantomSections", "PhantomSectionDirective", "depart_title", "setup", "visit_title"]

logger = logging.getLogger(__name__)


def visit_title(translator: LaTeXTranslator, node: nodes.title) -> None:
	"""
	Visit a :class:`docutils.nodes.title` node.

	:param translator:
	:param node: The node itself.
	"""

	if isinstance(node.parent, addnodes.seealso):
		# the environment already handles this
		raise nodes.SkipNode

	elif isinstance(node.parent, nodes.section):
		if translator.this_is_the_title:
			if len(node.children) != 1 and not isinstance(node.children[0], nodes.Text):
				logger.warning(__("document title is not a single Text node"), location=node)
			if not translator.elements["title"]:
				# text needs to be escaped since it is inserted into
				# the output literally
				translator.elements["title"] = translator.escape(node.astext())
			translator.this_is_the_title = 0
			raise nodes.SkipNode
		else:

			short = ''
			if node.traverse(nodes.image):
				short = f"[{translator.escape(' '.join(clean_astext(node).split()))}]"

			try:
				translator.body.append(fr'\{translator.sectionnames[translator.sectionlevel]}{short}{{')
			except IndexError:
				# just use "subparagraph", it's not numbered anyway
				translator.body.append(fr'\{translator.sectionnames[-1]}{short}{{')
			# breakpoint()
			translator.context.append(f'}}\n{translator.hypertarget_to(node.parent)}')

	elif isinstance(node.parent, nodes.topic):
		translator.body.append(r'\sphinxstyletopictitle{')
		translator.context.append('}\n')
	elif isinstance(node.parent, nodes.sidebar):
		translator.body.append(r'\sphinxstylesidebartitle{')
		translator.context.append('}\n')
	elif isinstance(node.parent, nodes.Admonition):
		translator.body.append('{')
		translator.context.append('}\n')
	elif isinstance(node.parent, nodes.table):
		# Redirect body output until title is finished.
		translator.pushbody([])
	else:
		logger.warning(
				__("encountered title node not in section, topic, table, admonition or sidebar"),
				location=node,
				)
		translator.body.append("\\sphinxstyleothertitle{")
		translator.context.append('}\n')

	translator.in_title = 1


def depart_title(translator: LaTeXTranslator, node: nodes.title) -> None:
	"""
	Depart a :class:`docutils.nodes.title` node.

	:param translator:
	:param node: The node itself.
	"""

	translator.in_title = 0
	if isinstance(node.parent, nodes.table):
		translator.table.caption = translator.popbody()
	else:
		translator.body.append(translator.context.pop())


class phantom_section_indicator(nodes.paragraph):
	pass


class PhantomSectionDirective(SphinxDirective):
	"""
	Sphinx directive for marking a section as being a phantom section.
	"""

	def run(self) -> List[nodes.Node]:  # noqa: D102
		return [phantom_section_indicator()]


class MarkPhantomSections(sphinx.transforms.SphinxTransform):
	"""
	Sphinx transform to mark the node, its parent and siblings as being a phantom section.
	"""

	default_priority = 999

	def apply(self, **kwargs) -> None:  # noqa: D102
		if not hasattr(self.env, "phantom_node_docnames"):
			self.env.phantom_node_docnames = set()

		for node in self.document.traverse(phantom_section_indicator):
			self.env.phantom_node_docnames.add(self.env.docname)
			node.parent.replace_self(node.parent.children[node.parent.children.index(node):])


def purge_outdated(app: Sphinx, env, added, changed, removed):
	return list(getattr(env, "phantom_node_docnames", []))


def setup(app: Sphinx):
	"""
	Setup Sphinx Extension.

	:param app:
	"""

	app.add_directive("phantom-section", PhantomSectionDirective)
	app.add_transform(MarkPhantomSections)
	app.add_node(nodes.title, override=True, latex=(visit_title, depart_title))
	app.connect("env-get-outdated", purge_outdated)

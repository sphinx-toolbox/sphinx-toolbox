#!/usr/bin/env python3
#
#  __init__.py
"""
Extensions to :mod:`sphinx.ext.autosummary`.

Provides an enhanced version of https://autodocsumm.readthedocs.io/
which respects the autodoc ``member-order`` option.
This can be given for an individual directive, in the
`autodoc_member_order <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_member_order>`_
configuration value, or via :confval:`autodocsumm_member_order`.

Also patches :class:`sphinx.ext.autosummary.Autosummary` to fix an issue where
the module name is sometimes duplicated.
I.e. ``foo.bar.baz()`` became ``foo.bar.foo.bar.baz()``, which of course doesn't exist
and so resulted in a broken link.


.. versionadded:: 0.7.0


.. confval:: autodocsumm_member_order
	:type: str
	:default: ``'alphabetical'``

	Determines the sort order of members in ``autodocsumm`` summary tables.
	Valid values are ``'alphabetical'`` and ``'bysource'``.

	Note that for ``'bysource'`` the module must be a Python module with the source code available.

The member order can also be set on a per-directive basis using the ``:member-order: [order]`` option.
This applies not only to :rst:dir:`automodule` etc. directives,
but also to :rst:dir:`automodulesumm` etc. directives.
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
#  Builds on top of https://github.com/Chilipp/autodocsumm
#  GPLv2 Licensed
#

# stdlib
import re
from typing import Any, Dict, List, Tuple

# 3rd party
import autodocsumm  # type: ignore
from domdf_python_tools.stringlist import StringList
from sphinx.application import Sphinx
from sphinx.config import ENUM
from sphinx.ext.autodoc import ClassDocumenter
from sphinx.ext.autosummary import Autosummary

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.utils import SphinxExtMetadata, allow_subclass_add, get_first_matching

__all__ = ["setup", "PatchedAutosummary", "PatchedAutoSummClassDocumenter"]


def add_autosummary(self):
	"""
	Add the :rst:dir:`autosummary` table of this documenter.
	"""

	if not self.options.autosummary:
		return

	content = StringList()
	content.indent_type = " " * 4
	sourcename = self.get_sourcename()
	grouped_documenters = self.get_grouped_documenters()

	for section, documenters in grouped_documenters.items():
		if not self.options.autosummary_no_titles:
			content.append(f"**{section}:**")

		content.blankline(ensure_single=True)

		content.append(".. autosummary::")
		content.blankline(ensure_single=True)

		member_order = get_first_matching(
				lambda x: x != "groupwise",
				[
						self.options.member_order,
						self.env.config.autodocsumm_member_order,
						self.env.config.autodoc_member_order,
						],
				default="alphabetical",
				)

		with content.with_indent_size(content.indent_size + 1):
			for documenter, _ in self.sort_members(documenters, member_order):
				content.append(f"~{documenter.fullname}")

		content.blankline()

	for line in content:
		self.add_line(line, sourcename)


class PatchedAutosummary(Autosummary):
	"""
	Pretty table containing short signatures and summaries of functions etc.

	Patched version of :class:`sphinx.ext.autosummary.Autosummary` to fix an issue where
	the module name is sometimes duplicated.

	I.e. ``foo.bar.baz()`` became ``foo.bar.foo.bar.baz()``, which of course doesn't exist
	and so resulted in a broken link.

	.. versionadded:: 0.5.1

	.. versionchanged:: 0.7.0

		Moved from :mod:`sphinx_toolbox.patched_autosummary`.
	"""

	def import_by_name(self, name: str, prefixes: List[str]) -> Tuple[str, Any, Any, str]:
		"""
		Import the object with the give name.

		:param name:
		:param prefixes:

		:return: The real name of the object, the object, the parent of the object, and the name of the module.
		"""

		real_name, obj, parent, modname = super().import_by_name(name=name, prefixes=prefixes)
		real_name = re.sub(rf"((?:{modname}\.)+)", f"{modname}.", real_name)
		return real_name, obj, parent, modname


class PatchedAutoSummClassDocumenter(autodocsumm.AutoSummClassDocumenter):
	"""
	Patched version of :class:`autodocsumm.AutoSummClassDocumenter`
	which doesn't show summary tables for aliased objects.

	.. versionadded:: 0.9.0
	"""  # noqa D400

	def add_content(self, *args, **kwargs):
		"""
		Add content from docstrings, attribute documentation and user.
		"""

		ClassDocumenter.add_content(self, *args, **kwargs)

		if not self.doc_as_attr:
			self.add_autosummary()


def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autosummary`.

	:param app: The Sphinx app.
	"""

	app.setup_extension("sphinx.ext.autosummary")
	app.setup_extension("autodocsumm")

	# app.add_directive('autosummary', PatchedAutosummary, override=True)

	autodocsumm.AutosummaryDocumenter.add_autosummary = add_autosummary

	allow_subclass_add(app, PatchedAutoSummClassDocumenter)

	app.add_config_value(
			"autodocsumm_member_order",
			"alphabetical",
			True,
			ENUM("alphabetic", "alphabetical", "bysource"),
			)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

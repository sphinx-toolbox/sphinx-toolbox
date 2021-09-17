#!/usr/bin/env python3
#
#  __init__.py
r"""
Extensions to :mod:`sphinx.ext.autosummary`.

Provides an enhanced version of https://autodocsumm.readthedocs.io/
which respects the autodoc ``member-order`` option.
This can be given for an individual directive, in the
`autodoc_member_order <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_member_order>`_
configuration value, or via :confval:`autodocsumm_member_order`.

Also patches :class:`sphinx.ext.autosummary.Autosummary` to fix an issue where
the module name is sometimes duplicated.
I.e. ``foo.bar.baz()`` became ``foo.bar.foo.bar.baz()``, which of course doesn't exist
and created a broken link.


.. versionadded:: 0.7.0

.. versionchanged:: 1.3.0

	Autosummary now selects the appropriate documenter for attributes rather than
	falling back to :class:`~sphinx.ext.autodoc.DataDocumenter`.

.. versionchanged:: 2.13.0

	Also patches :class:`sphinx.ext.autodoc.ModuleDocumenter` to fix an issue where
	``__all__`` is not respected for autosummary tables.



Configuration
--------------

.. confval:: autodocsumm_member_order
	:type: :py:obj:`str`
	:default: ``'alphabetical'``

	Determines the sort order of members in ``autodocsumm`` summary tables.
	Valid values are ``'alphabetical'`` and ``'bysource'``.

	Note that for ``'bysource'`` the module must be a Python module with the source code available.

	The member order can also be set on a per-directive basis using the ``:member-order: [order]`` option.
	This applies not only to :rst:dir:`automodule` etc. directives,
	but also to :rst:dir:`automodulesumm` etc. directives.

.. confval:: autosummary_col_type
	:type: :py:obj:`str`
	:default: ``'\X'``

	The LaTeX column type to use for autosummary tables.

	Custom columns can be defined in the LaTeX preamble for use with this option.

	For example:

	.. code-block:: python

		latex_elements["preamble"] = r'''
			\makeatletter
			\newcolumntype{\Xx}[2]{>{\raggedright\arraybackslash}p{\dimexpr
				(\linewidth-\arrayrulewidth)*#1/#2-\tw@\tabcolsep-\arrayrulewidth\relax}}
			\makeatother
			'''

		autosummary_col_type = "\\Xx"


	.. versionadded:: 2.13.0


.. latex:clearpage::


API Reference
----------------

"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
#  Builds on top of, and PatchedAutoDocSummDirective based on, https://github.com/Chilipp/autodocsumm
#  | Copyright 2016-2019, Philipp S. Sommer
#  | Copyright 2020-2021, Helmholtz-Zentrum Hereon
#  |
#  | Licensed under the Apache License, Version 2.0 (the "License");
#  | you may not use this file except in compliance with the License.
#  | You may obtain a copy of the License at
#  |
#  |     http://www.apache.org/licenses/LICENSE-2.0
#  |
#  | Unless required by applicable law or agreed to in writing,
#  | software distributed under the License is distributed on an "AS IS" BASIS,
#  | WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  | See the License for the specific language governing permissions and limitations under the License.
#

# stdlib
import inspect
import operator
import re
from typing import Any, List, Optional, Tuple, Type

# 3rd party
import autodocsumm  # type: ignore
import sphinx
from docutils import nodes
from domdf_python_tools.stringlist import StringList
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.config import ENUM
from sphinx.ext.autodoc import (
		ALL,
		INSTANCEATTR,
		ClassDocumenter,
		Documenter,
		ModuleDocumenter,
		logger,
		special_member_re
		)
from sphinx.ext.autodoc.directive import DocumenterBridge, process_documenter_options
from sphinx.ext.autodoc.importer import get_module_members
from sphinx.ext.autosummary import Autosummary, FakeDirective
from sphinx.locale import __
from sphinx.util.inspect import getdoc, safe_getattr

# this package
from sphinx_toolbox._data_documenter import DataDocumenter
from sphinx_toolbox.more_autodoc import ObjectMembers
from sphinx_toolbox.utils import SphinxExtMetadata, allow_subclass_add, get_first_matching, metadata_add_version

if sphinx.version_info > (4, 1):
	# 3rd party
	from sphinx.util.docstrings import separate_metadata
else:
	# 3rd party
	from sphinx.util.docstrings import extract_metadata

__all__ = [
		"PatchedAutosummary",
		"PatchedAutoSummModuleDocumenter",
		"PatchedAutoSummClassDocumenter",
		"get_documenter",
		"setup",
		]


def add_autosummary(self):
	"""
	Add the :rst:dir:`autosummary` table of this documenter.
	"""

	if not self.options.get("autosummary", False):
		return

	content = StringList()
	content.indent_type = ' ' * 4
	sourcename = self.get_sourcename()
	grouped_documenters = self.get_grouped_documenters()

	if not self.options.get("autosummary-no-titles", False) and grouped_documenters:
		content.blankline()
		content.append(".. latex:vspace:: 10px")
		content.blankline()

	for section, documenters in grouped_documenters.items():
		if not self.options.get("autosummary-no-titles", False):
			content.append(f"**{section}:**")
			content.blankline()
			content.append(".. latex:vspace:: -5px")

		content.blankline(ensure_single=True)

		# TODO transform to make caption associated with table in LaTeX

		content.append(".. autosummary::")
		content.blankline(ensure_single=True)

		member_order = get_first_matching(
				lambda x: x != "groupwise",
				[
						self.options.get("member-order", ''),
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
	and created a broken link.

	.. versionadded:: 0.5.1
	.. versionchanged:: 0.7.0  Moved from :mod:`sphinx_toolbox.patched_autosummary`.

	.. versionchanged:: 2.13.0

		Added support for customising the column type with the :confval:`autosummary_col_type` option.
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

	def create_documenter(
			self,
			app: Sphinx,
			obj: Any,
			parent: Any,
			full_name: str,
			) -> Documenter:
		"""
		Get an :class:`autodoc.Documenter` class suitable for documenting the given object.

		:param app: The Sphinx application.
		:param obj: The object being documented.
		:param parent: The parent of the object (e.g. a module or a class).
		:param full_name: The full name of the object.

		.. versionchanged:: 1.3.0

			Now selects the appropriate documenter for attributes rather than
			falling back to :class:`~sphinx.ext.autodoc.DataDocumenter`.

		:rtype:

		.. clearpage::
		"""

		doccls = get_documenter(app, obj, parent)
		return doccls(self.bridge, full_name)

	def get_table(self, items: List[Tuple[str, str, str, str]]) -> List[nodes.Node]:
		"""
		Generate a list of table nodes for the :rst:dir:`autosummary` directive.

		:param items: A list  produced by ``self.get_items``.
		"""

		table_spec, *other_nodes = super().get_table(items)
		assert isinstance(table_spec, addnodes.tabular_col_spec)

		column_type = getattr(self.env.config, "autosummary_col_type", r"\X")
		table_spec["spec"] = f'{column_type}{{1}}{{2}}{column_type}{{1}}{{2}}'

		return [table_spec, *other_nodes]


def get_documenter(app: Sphinx, obj: Any, parent: Any) -> Type[Documenter]:
	"""
	Returns an :class:`autodoc.Documenter` class suitable for documenting the given object.

	.. versionadded:: 1.3.0

	:param app: The Sphinx application.
	:param obj: The object being documented.
	:param parent: The parent of the object (e.g. a module or a class).
	"""

	if inspect.ismodule(obj):
		# ModuleDocumenter.can_document_member always returns False
		return ModuleDocumenter

	# Construct a fake documenter for *parent*
	if parent is not None:
		parent_doc_cls = get_documenter(app, parent, None)
	else:
		parent_doc_cls = ModuleDocumenter

	if hasattr(parent, "__name__"):
		parent_doc = parent_doc_cls(FakeDirective(), parent.__name__)
	else:
		parent_doc = parent_doc_cls(FakeDirective(), '')

	# Get the correct documenter class for *obj*
	classes = [
			cls for cls in app.registry.documenters.values()
			if cls.can_document_member(obj, '', False, parent_doc)
			]

	data_doc_classes = [
			cls for cls in app.registry.documenters.values() if cls.can_document_member(obj, '', True, parent_doc)
			]

	if classes:
		classes.sort(key=lambda cls: cls.priority)
		return classes[-1]
	elif data_doc_classes:
		data_doc_classes.sort(key=lambda cls: cls.priority)
		return data_doc_classes[-1]
	else:
		return DataDocumenter


class PatchedAutoSummModuleDocumenter(autodocsumm.AutoSummModuleDocumenter):
	"""
	Patched version of :class:`autodocsumm.AutoSummClassDocumenter`
	which works around a bug in Sphinx 3.4 and above where ``__all__`` is not respected.

	.. versionadded:: 2.13.0
	"""  # noqa: D400

	def filter_members(self, members: ObjectMembers, want_all: bool) -> List[Tuple[str, Any, bool]]:
		"""
		Filter the given member list.

		Members are skipped if:

		* they are private (except if given explicitly or the ``private-members`` option is set)
		* they are special methods (except if given explicitly or the ``special-members`` option is set)
		* they are undocumented (except if the ``undoc-members`` option is set)

		The user can override the skipping decision by connecting to the :event:`autodoc-skip-member` event.
		"""

		def is_filtered_inherited_member(name: str) -> bool:
			if inspect.isclass(self.object):
				for cls in self.object.__mro__:
					if cls.__name__ == self.options.inherited_members and cls != self.object:
						# given member is a member of specified *super class*
						return True
					elif name in cls.__dict__:
						return False
					elif name in self.get_attr(cls, "__annotations__", {}):
						return False

			return False

		ret = []

		# search for members in source code too
		namespace = '.'.join(self.objpath)  # will be empty for modules

		if self.analyzer:
			attr_docs = self.analyzer.find_attr_docs()
		else:
			attr_docs = {}

		doc: Optional[str]

		# process members and determine which to skip
		for (membername, member) in members:
			# if isattr is True, the member is documented as an attribute
			if member is INSTANCEATTR or (namespace, membername) in attr_docs:
				isattr = True
			else:
				isattr = False

			doc = getdoc(
					member,
					self.get_attr,
					self.env.config.autodoc_inherit_docstrings,
					self.parent,
					self.object_name
					)
			if not isinstance(doc, str):
				# Ignore non-string __doc__
				doc = None

			# if the member __doc__ is the same as self's __doc__, it's just
			# inherited and therefore not the member's doc
			cls = self.get_attr(member, "__class__", None)
			if cls:
				cls_doc = self.get_attr(cls, "__doc__", None)
				if cls_doc == doc:
					doc = None

			if sphinx.version_info > (4, 1):
				doc, metadata = separate_metadata(doc)  # type: ignore
			else:
				metadata = extract_metadata(doc)  # type: ignore

			has_doc = bool(doc)

			if "private" in metadata:
				# consider a member private if docstring has "private" metadata
				isprivate = True
			elif "public" in metadata:
				# consider a member public if docstring has "public" metadata
				isprivate = False
			else:
				isprivate = membername.startswith('_')

			keep = False
			if safe_getattr(member, "__sphinx_mock__", False):
				# mocked module or object
				pass
			elif self.options.exclude_members and membername in self.options.exclude_members:
				# remove members given by exclude-members
				keep = False
			elif want_all and special_member_re.match(membername):
				# special __methods__
				if self.options.special_members and membername in self.options.special_members:
					if membername == "__doc__":
						keep = False
					elif is_filtered_inherited_member(membername):
						keep = False
					else:
						keep = has_doc or self.options.undoc_members
				else:
					keep = False
			elif (namespace, membername) in attr_docs:
				if want_all and isprivate:
					if self.options.private_members is None:
						keep = False
					else:
						keep = membername in self.options.private_members
				else:
					# keep documented attributes
					keep = True
				isattr = True
			elif want_all and isprivate:
				if has_doc or self.options.undoc_members:
					if self.options.private_members is None:
						keep = False
					elif is_filtered_inherited_member(membername):
						keep = False
					else:
						keep = membername in self.options.private_members
				else:
					keep = False
			else:
				if self.options.members is ALL and is_filtered_inherited_member(membername):
					keep = False
				else:
					# ignore undocumented members if :undoc-members: is not given
					keep = has_doc or self.options.undoc_members

			# give the user a chance to decide whether this member
			# should be skipped
			if self.env.app:
				# let extensions preprocess docstrings
				try:
					skip_user = self.env.app.emit_firstresult(
							"autodoc-skip-member",
							self.objtype,
							membername,
							member,
							not keep,
							self.options,
							)
					if skip_user is not None:
						keep = not skip_user
				except Exception as exc:
					msg = 'autodoc: failed to determine %r to be documented, the following exception was raised:\n%s'
					logger.warning(__(msg), member, exc, type="autodoc")
					keep = False

			if keep:
				ret.append((membername, member, isattr))

		return ret

	def get_object_members(self, want_all: bool) -> Tuple[bool, ObjectMembers]:
		"""
		Return a tuple of  ``(members_check_module, members)``,
		where ``members`` is a list of ``(membername, member)`` pairs of the members of ``self.object``.

		If ``want_all`` is :py:obj:`True`, return all members.
		Otherwise, only return those members given by ``self.options.members`` (which may also be none).
		"""  # noqa: D400

		if want_all:
			if self.__all__:
				memberlist = self.__all__
			else:
				# for implicit module members, check __module__ to avoid
				# documenting imported objects
				return True, get_module_members(self.object)
		else:
			memberlist = self.options.members or []
		ret = []
		for mname in memberlist:
			try:
				ret.append((mname, safe_getattr(self.object, mname)))
			except AttributeError:
				logger.warning(
						operator.mod(
								__("missing attribute mentioned in :members: or __all__: module %s, attribute %s"),
								(safe_getattr(self.object, "__name__", "???"), mname),
								),
						type="autodoc"
						)
		return False, ret


class PatchedAutoSummClassDocumenter(autodocsumm.AutoSummClassDocumenter):
	"""
	Patched version of :class:`autodocsumm.AutoSummClassDocumenter`
	which doesn't show summary tables for aliased objects.

	.. versionadded:: 0.9.0
	"""  # noqa: D400

	def add_content(self, *args, **kwargs):
		"""
		Add content from docstrings, attribute documentation and user.
		"""

		ClassDocumenter.add_content(self, *args, **kwargs)

		if not self.doc_as_attr:
			self.add_autosummary()


class PatchedAutoDocSummDirective(autodocsumm.AutoDocSummDirective):
	"""
	Patched ``AutoDocSummDirective`` which uses :py:obj:`None` for the members option rather than an empty string.

	.. attention:: This class is not part of the public API.
	"""

	def run(self):
		reporter = self.state.document.reporter

		if hasattr(reporter, "get_source_and_line"):
			source, lineno = reporter.get_source_and_line(self.lineno)
		else:
			source, lineno = (None, None)

		# look up target Documenter
		objtype = self.name[4:-4]  # strip prefix (auto-) and suffix (-summ).
		doccls = self.env.app.registry.documenters[objtype]

		self.options["autosummary-force-inline"] = "True"
		self.options["autosummary"] = "True"
		if "no-members" not in self.options:
			self.options["members"] = None

		# process the options with the selected documenter's option_spec
		try:
			documenter_options = process_documenter_options(doccls, self.config, self.options)
		except (KeyError, ValueError, TypeError) as exc:
			# an option is either unknown or has a wrong type
			logger.error(
					"An option to %s is either unknown or has an invalid value: %s",
					self.name,
					exc,
					location=(self.env.docname, lineno),
					)
			return []

		# generate the output
		params = DocumenterBridge(self.env, reporter, documenter_options, lineno, self.state)
		documenter = doccls(params, self.arguments[0])
		documenter.add_autosummary()

		node = nodes.paragraph()
		node.document = self.state.document
		self.state.nested_parse(params.result, 0, node)

		return node.children


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autosummary`.

	:param app: The Sphinx application.
	"""

	app.setup_extension("sphinx.ext.autosummary")
	app.setup_extension("autodocsumm")

	app.add_directive("autosummary", PatchedAutosummary, override=True)
	app.add_directive("autoclasssumm", PatchedAutoDocSummDirective, override=True)
	app.add_directive("automodulesumm", PatchedAutoDocSummDirective, override=True)

	autodocsumm.AutosummaryDocumenter.add_autosummary = add_autosummary
	allow_subclass_add(app, PatchedAutoSummModuleDocumenter)
	allow_subclass_add(app, PatchedAutoSummClassDocumenter)

	app.add_config_value(
			"autodocsumm_member_order",
			default="alphabetical",
			rebuild=True,
			types=ENUM("alphabetic", "alphabetical", "bysource"),
			)

	app.add_config_value(
			"autosummary_col_type",
			default=r"\X",
			rebuild="latex",
			types=[str],
			)

	return {"parallel_read_safe": True}

#!/usr/bin/env python3
#
#  autotypeddict.py
"""
A Sphinx directive for documenting :class:`TypedDicts <typing.TypedDict>` in Python.

Provides the :rst:dir:`autotypeddict` directive to document a :class:`typing.TypedDict`.
It behaves much like :rst:dir:`autoclass` and :rst:dir:`autofunction`.

Only supports :mod:`typing_extensions`\\'s TypedDict until :pull:`700 <python/typing>` is implemented in CPython.

.. versionadded:: 0.5.0

See also https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html .
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

# stdlib
from typing import Any, Callable, Dict, List, Optional, Tuple, Type

# 3rd party
from domdf_python_tools.stringlist import StringList
from sphinx.application import Sphinx
from sphinx.domains import ObjType
from sphinx.domains.python import PyClasslike, PyXRefRole
from sphinx.ext.autodoc import INSTANCEATTR, ClassDocumenter, Documenter, bool_option
from sphinx.pycode import ModuleAnalyzer
from sphinx.util.inspect import getdoc, safe_getattr

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.autodoc_helpers import begin_generate, filter_members_warning
from sphinx_toolbox.autodoc_typehints import format_annotation
from sphinx_toolbox.utils import flag

__all__ = ["TypedDictDocumenter", "setup"]


class TypedDictDocumenter(ClassDocumenter):
	r"""
	Sphinx autodoc :class:`~sphinx.ext.autodoc.Documenter`
	for documenting :class:`typing.TypedDict`\s.

	.. versionadded:: 0.5.0
	"""

	objtype = "typeddict"
	directivetype = "typeddict"
	priority = 20
	option_spec: Dict[str, Callable] = {
			'noindex': bool_option,
			'alphabetical': flag,
			}

	def __init__(self, *args: Any) -> None:
		super().__init__(*args)

		alphabetical = self.options.get("alphabetical", False)
		if alphabetical:
			self.options["member-order"] = "alphabetical"
		else:
			self.options["member-order"] = "bysource"

	@classmethod
	def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
		"""
		Called to see if a member can be documented by this documenter.

		:param member:
		:param membername:
		:param isattr:
		:param parent:
		"""

		for attr in {"__optional_keys__", "__required_keys__", "__total__"}:
			if not hasattr(member, attr):
				return False

		return True

	def format_signature(self, **kwargs: Any) -> str:
		"""
		Typed Dicts do not have a signature.
		"""

		return ''  # pragma: no cover

	def generate(
			self,
			more_content: Optional[Any] = None,
			real_modname: Optional[str] = None,
			check_module: bool = False,
			all_members: bool = False,
			) -> None:
		"""
		Generate reST for the object given by ``self.name``, and possibly for its members.

		:param more_content: Additional content to include in the reST output.
		:param real_modname: Module name to use to find attribute documentation.
		:param check_module: If :py:obj:`True`, only generate if the object is defined
			in the module name it is imported from.
		:param all_members: If :py:obj:`True`, document all members.
		"""

		ret = begin_generate(self, real_modname, check_module)
		if ret is None:
			return
		sourcename = ret

		# Set sourcename as instance variable to avoid passing it around; it will get deleted later
		self.sourcename = sourcename

		# make sure that the result starts with an empty line.  This is
		# necessary for some situations where another directive preprocesses
		# reST and no starting newline is present
		self.add_line('', sourcename)

		# generate the directive header and options, if applicable
		self.add_directive_header('')
		self.add_line('', sourcename)

		# e.g. the module directive doesn't have content
		self.indent += self.content_indent

		# add all content (from docstrings, attribute docs etc.)
		self.add_content(more_content)

		if not getdoc(self.object):
			self.add_line(":class:`typing.TypedDict`.", sourcename)
			self.add_line('', sourcename)

		# document members, if possible
		self.document_members(True)
		del self.sourcename

	def sort_members(
			self,
			documenters: List[Tuple[Documenter, bool]],
			order: str,
			) -> List[Tuple[Documenter, bool]]:
		"""
		Sort the TypedDict's members.

		:param documenters:
		:param order:

		:return:
		"""

		# The documenters for the keys, in the desired order
		documenters = super().sort_members(documenters, order)

		# Mapping of key names to docstrings (as list of strings)
		docstrings = {
				k[1]: v
				for k, v in ModuleAnalyzer.for_module(self.object.__module__).find_attr_docs().items()
				}

		required_keys = []
		optional_keys = []
		types = self.object.__annotations__

		for d in documenters:
			name = d[0].name.split(".")[-1]
			if name in self.object.__required_keys__:
				required_keys.append(name)
			elif name in self.object.__optional_keys__:
				optional_keys.append(name)
			# else: warn user. This shouldn't ever happen, though.

		if required_keys:
			self.add_line('', self.sourcename)
			self.add_line(":Required Keys:", self.sourcename)
			self.document_keys(required_keys, types, docstrings)
			self.add_line('', self.sourcename)

		if optional_keys:
			self.add_line('', self.sourcename)
			self.add_line(":Optional Keys:", self.sourcename)
			self.document_keys(optional_keys, types, docstrings)
			self.add_line('', self.sourcename)

		return []

	def document_keys(self, keys: List[str], types: Dict[str, Type], docstrings: Dict[str, List[str]]):
		"""
		Document keys in a :class:`typing.TypedDict`.

		:param keys: List of key names to document.
		:param types: Mapping of key names to types.
		:param docstrings: Mapping of key names to docstrings.
		"""

		content = StringList()

		for key in keys:
			if key in types:
				key_type = f"({format_annotation(types[key])}) "
			else:
				key_type = ''

			content.append(f"    * **{key}** {key_type}-- {' '.join(docstrings.get(key, ''))}")

		for line in content:
			self.add_line(line, self.sourcename)

	def filter_members(
			self,
			members: List[Tuple[str, Any]],
			want_all: bool,
			) -> List[Tuple[str, Any, bool]]:
		"""
		Filter the given member list.

		:param members:
		:param want_all:
		"""

		ret = []

		# process members and determine which to skip
		for (membername, member) in members:
			# if isattr is True, the member is documented as an attribute

			if safe_getattr(member, "__sphinx_mock__", False):
				# mocked module or object
				keep = False
			elif membername.startswith('_'):
				keep = False
			else:
				keep = True

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
					filter_members_warning(member, exc)
					keep = False

			if keep:
				ret.append((membername, member, member is INSTANCEATTR))

		return ret


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup :mod:`sphinx_toolbox.autotypeddict`.

	:param app:

	.. versionadded:: 0.5.0
	"""

	app.registry.domains["py"].object_types["typeddict"] = ObjType("typeddict", "typeddict", "class", "obj")
	app.add_directive_to_domain("py", "typeddict", PyClasslike)
	app.add_role_to_domain("py", "typeddict", PyXRefRole())

	app.add_autodocumenter(TypedDictDocumenter)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

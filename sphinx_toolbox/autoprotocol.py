#!/usr/bin/env python3
#
#  autoprotocol.py
"""
A Sphinx directive for documenting Protocols in Python.

Provides the ``.. autoprotocol::`` directive to document a :class:`~typing.Protocol`.
It behaves much like ``.. autoclass::`` and ``.. autofunction::``.

.. versionadded:: 0.2.0
"""
#
# See also https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
#
#  Copyright (c) 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
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
import sys
from typing import Any, Dict, List, Optional, Tuple

# 3rd party
from sphinx.application import Sphinx
from sphinx.domains import ObjType
from sphinx.domains.python import PyClasslike, PyXRefRole
from sphinx.ext.autodoc import INSTANCEATTR, ClassDocumenter
from sphinx.locale import _
from sphinx.util.inspect import getdoc, safe_getattr

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.autodoc_helpers import begin_generate, filter_members_warning

if sys.version_info < (3, 8):  # pragma: no cover (>=py38)
	# 3rd party
	from typing_extensions import _ProtocolMeta  # type: ignore
else:  # pragma: no cover (<py38)
	# stdlib
	from typing import _ProtocolMeta  # type: ignore

__all__ = ["ProtocolDocumenter", "setup"]

globally_excluded_methods = {
		"__dict__",
		"__class__",
		"__dir__",
		"__weakref__",
		"__module__",
		"__annotations__",
		"__orig_bases__",
		"__parameters__",
		"__subclasshook__",
		"__init_subclass__",
		"__attrs_attrs__",
		"__init__",
		"__getnewargs__",
		"__abstractmethods__",
		"__doc__",
		"__abstractmethods__",
		"__args__",
		"__class__",
		"__delattr__",
		"__dir__",
		"__extra__",
		"__module__",
		"__next_in_mro__",
		"__orig_bases__",
		"__origin__",
		"__parameters__",
		"__subclasshook__",
		"__tree_hash__",
		}


class ProtocolDocumenter(ClassDocumenter):
	r"""
	Sphinx autodoc :class:`~sphinx.ext.autodoc.Documenter` for documenting :class:`~enum.Enum`\s.

	.. versionadded:: 0.2.0
	"""

	objtype = "protocol"
	directivetype = "protocol"
	priority = 20

	@classmethod
	def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
		"""
		Called to see if a member can be documented by this documenter.

		:param member:
		:param membername:
		:param isattr:
		:param parent:
		"""

		return isinstance(member, _ProtocolMeta)

	def format_signature(self, **kwargs: Any) -> str:
		"""
		Protocols do not have a signature.
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
		Generate reST for the object given by *self.name*, and possibly for its members.

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
			self.add_line(":class:`typing.Protocol`.", sourcename)
			self.add_line('', sourcename)

		self.add_line("Classes that implement this protocol must have the following methods:", sourcename)
		self.add_line('', sourcename)

		# document members, if possible
		# self.options.special_members = []
		# self.options.undoc_members = []
		self.document_members(True)

	def filter_members(
			self,
			members: List[Tuple[str, Any]],
			want_all: bool,
			) -> List[Tuple[str, Any, bool]]:
		"""
		Filter the given member list.

		:param members:
		:param want_all:
		:return:
		"""

		ret = []

		# process members and determine which to skip
		for (membername, member) in members:
			# if isattr is True, the member is documented as an attribute

			if safe_getattr(member, "__sphinx_mock__", False):
				# mocked module or object
				keep = False

			elif self.options.exclude_members and membername in self.options.exclude_members:
				# remove members given by exclude-members
				keep = False

			elif membername.startswith('_') and not (membername.startswith("__") and membername.endswith("__")):
				keep = False

			elif membername not in globally_excluded_methods:
				# Magic method you wouldn't overload, or private method.
				if membername in dir(self.object.__base__):
					keep = member is not getattr(self.object.__base__, membername)
				else:
					keep = True

			else:
				keep = False

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
	Setup ``sphinx-toolbox.autoprocotol``.

	:param app:

	.. versionadded:: 0.2.0
	"""

	app.registry.domains["py"].object_types["protocol"] = ObjType(_("protocol"), "protocol", "class", "obj")
	app.add_directive_to_domain("py", "protocol", PyClasslike)
	app.add_role_to_domain("py", "protocol", PyXRefRole())

	app.add_autodocumenter(ProtocolDocumenter)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

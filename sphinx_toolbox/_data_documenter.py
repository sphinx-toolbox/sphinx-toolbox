#!/usr/bin/env python3
#
#  _data_documenter.py
"""
Relevant parts of :mod:`sphinx.ext.autodoc` from Sphinx 3.3.1.
"""
#
#  Based on Sphinx
#  Copyright (c) 2007-2020 by the Sphinx team.
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
from typing import Any, get_type_hints

# 3rd party
from sphinx.ext.autodoc import (
		SUPPRESS,
		UNINITIALIZED_ATTR,
		ModuleDocumenter,
		ModuleLevelDocumenter,
		annotation_option
		)
from sphinx.util import logging
from sphinx.util.inspect import object_description, safe_getattr
from sphinx.util.typing import stringify as stringify_typehint

__all__ = ["DataDocumenter"]

logger = logging.getLogger(__name__)


class DataDocumenter(ModuleLevelDocumenter):
	"""
	Specialized Documenter subclass for data items.
	"""

	objtype = "data"
	member_order = 40
	priority = -10
	option_spec = dict(ModuleLevelDocumenter.option_spec)
	option_spec["annotation"] = annotation_option

	@classmethod
	def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
		"""
		Called to see if a member can be documented by this documenter.
		"""

		return isinstance(parent, ModuleDocumenter) and isattr

	def add_directive_header(self, sig: str) -> None:  # pragma: no cover (<Py37)
		"""
		Add the directive header and options to the generated content.
		"""

		super().add_directive_header(sig)
		sourcename = self.get_sourcename()
		if not self.options.annotation:
			# obtain annotation for this data
			try:
				annotations = get_type_hints(self.parent)
			except NameError:
				# Failed to evaluate ForwardRef (maybe TYPE_CHECKING)
				annotations = safe_getattr(self.parent, "__annotations__", {})
			except TypeError:
				annotations = {}
			except KeyError:
				# a broken class found (refs: https://github.com/sphinx-doc/sphinx/issues/8084)
				annotations = {}
			except AttributeError:
				# AttributeError is raised on 3.5.2 (fixed by 3.5.3)
				annotations = {}

			if self.objpath[-1] in annotations:
				objrepr = stringify_typehint(annotations.get(self.objpath[-1]))
				self.add_line("   :type: " + objrepr, sourcename)
			else:
				key = ('.'.join(self.objpath[:-1]), self.objpath[-1])
				if self.analyzer and key in self.analyzer.annotations:
					self.add_line("   :type: " + self.analyzer.annotations[key], sourcename)

			try:
				if self.object is UNINITIALIZED_ATTR:
					pass
				else:
					objrepr = object_description(self.object)
					self.add_line("   :value: " + objrepr, sourcename)
			except ValueError:
				pass
		elif self.options.annotation is SUPPRESS:
			pass
		else:
			self.add_line("   :annotation: %s" % self.options.annotation, sourcename)

	def document_members(self, all_members: bool = False) -> None:  # noqa: D102
		pass

	def get_real_modname(self) -> str:
		"""
		Get the real module name of an object to document.

		It can differ from the name of the module through which the object was imported.
		"""

		return self.get_attr(self.parent or self.object, "__module__", None) or self.modname

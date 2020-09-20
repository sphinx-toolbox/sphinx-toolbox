#!/usr/bin/env python3
#
#  variables.py
r"""
Documenter for module level variables, similar to :rst:dir:`autodata` but
with a different appearance and more customisation options.

.. extensions:: sphinx_toolbox.more_autodoc.variables

.. versionadded:: 0.6.0

.. versionchanged:: 0.7.0

	Added ``*AttributeDocumenter``\s
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
import importlib
from typing import Any, Dict, get_type_hints

# 3rd party
import sphinx.ext.autodoc
from sphinx.application import Sphinx
from sphinx.ext.autodoc import (
		INSTANCEATTR,
		UNINITIALIZED_ATTR,
		AttributeDocumenter,
		ClassLevelDocumenter,
		DataDocumenter,
		Documenter,
		ModuleDocumenter,
		ModuleLevelDocumenter
		)
from sphinx.util.inspect import object_description, safe_getattr

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc.typehints import format_annotation
from sphinx_toolbox.utils import SphinxExtMetadata, flag

__all__ = [
		"VariableDocumenter",
		"TypedAttributeDocumenter",
		"InstanceAttributeDocumenter",
		"type_template",
		"get_variable_type",
		"setup",
		]


def get_variable_type(documenter: Documenter) -> str:
	"""
	Returns the type annotation for a variable.

	:param documenter:
	"""

	try:
		annotations = get_type_hints(documenter.parent)
	except NameError:
		# Failed to evaluate ForwardRef (maybe TYPE_CHECKING)
		annotations = safe_getattr(documenter.parent, "__annotations__", {})
	except TypeError:
		annotations = {}
	except KeyError:
		# a broken class found (refs: https://github.com/sphinx-doc/sphinx/issues/8084)
		annotations = {}
	except AttributeError:
		# AttributeError is raised on 3.5.2 (fixed by 3.5.3)
		annotations = {}

	if documenter.objpath[-1] in annotations:
		return format_annotation(annotations.get(documenter.objpath[-1]))
	else:
		key = ('.'.join(documenter.objpath[:-1]), documenter.objpath[-1])
		if documenter.analyzer and key in documenter.analyzer.annotations:
			return documenter.analyzer.annotations[key]

		else:
			return ''


type_template = "   **Type:** |nbsp| |nbsp| |nbsp| |nbsp| %s"
"""
Template for rendering type annotations in :class:`~.VariableDocumenter`,
:class:`~.TypedAttributeDocumenter` and :class:`~.InstanceAttributeDocumenter`.

Renders like:

	**Type:** |nbsp| |nbsp| |nbsp| |nbsp| :class:`str`

"""


class VariableDocumenter(DataDocumenter):
	"""
	Specialized Documenter subclass for data items.
	"""

	directivetype = "data"
	objtype = "variable"
	priority = DataDocumenter.priority + 1
	option_spec = {
			"no-value": flag,
			"no-type": flag,
			"type": str,
			"value": str,
			**DataDocumenter.option_spec,
			}

	def add_directive_header(self, sig: str):
		"""
		Add the directive's header.

		:param sig:
		"""

		sourcename = self.get_sourcename()

		no_value = self.options.get("no-value", False)
		no_type = self.options.get("no-type", False)

		if not self.options.annotation:
			ModuleLevelDocumenter.add_directive_header(self, sig)

			if not no_value:
				if "value" in self.options:
					self.add_line(f"   :value: {self.options['value']}", sourcename)
				else:
					try:
						if self.object is not UNINITIALIZED_ATTR:
							objrepr = object_description(self.object)
							self.add_line(f"   :value: {objrepr}", sourcename)
					except ValueError:
						pass

			self.add_line('', sourcename)

			if not no_type:
				if "type" in self.options:
					self.add_line(type_template % self.options["type"], sourcename)
				else:
					# obtain type annotation for this data
					the_type = get_variable_type(self)
					if not the_type.strip():
						try:
							the_type = format_annotation(type(self.object))
						except Exception:
							return

					line = type_template % the_type
					self.add_line(line, sourcename)

		else:
			super().add_directive_header(sig)


class TypedAttributeDocumenter(AttributeDocumenter):
	"""
	Alternative version of :class:`sphinx.ext.autodoc.AttributeDocumenter`
	with better type hint rendering.

	Specialized Documenter subclass for attributes.

	.. versionadded:: 0.7.0

	.. versionchanged:: 1.0.0

		Now uses the type of the variable if it is not explicitly annotated.
	"""  # noqa D400

	def add_directive_header(self, sig: str):
		"""
		Add the directive's header.

		:param sig:
		"""

		sourcename = self.get_sourcename()

		no_value = self.options.get("no-value", False)
		no_type = self.options.get("no-type", False)

		if not self.options.annotation:
			ClassLevelDocumenter.add_directive_header(self, sig)

			# data descriptors do not have useful values
			if not no_value and not self._datadescriptor:
				if "value" in self.options:
					self.add_line("   :value: " + self.options["value"], sourcename)
				else:
					try:
						if self.object is not INSTANCEATTR:
							objrepr = object_description(self.object)
							self.add_line("   :value: " + objrepr, sourcename)
					except ValueError:
						pass

			self.add_line('', sourcename)

			if not no_type:
				if "type" in self.options:
					self.add_line(type_template % self.options["type"], sourcename)
				else:
					# obtain type annotation for this attribute
					the_type = get_variable_type(self)
					if not the_type.strip():
						try:
							the_type = format_annotation(type(self.object))
						except Exception:
							return

					line = type_template % the_type
					self.add_line(line, sourcename)

		else:
			super().add_directive_header(sig)


class InstanceAttributeDocumenter(TypedAttributeDocumenter):
	"""
	Alternative version of :class:`sphinx.ext.autodoc.InstanceAttributeDocumenter`
	with better type hint rendering.

	Specialized Documenter subclass for attributes that cannot be imported
	because they are instance attributes (e.g. assigned in ``__init__``).

	.. versionadded:: 0.7.0

	.. versionchanged:: 1.0.0

		Now uses the type of the variable if it is not explicitly annotated.
	"""  # noqa D400

	objtype = sphinx.ext.autodoc.InstanceAttributeDocumenter.objtype
	directivetype = sphinx.ext.autodoc.InstanceAttributeDocumenter.directivetype
	member_order = 60

	# must be higher than TypedAttributeDocumenter
	priority = 11

	@classmethod
	def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
		"""
		Called to see if a member can be documented by this documenter.

		This documenter only documents INSTANCEATTR members.

		:param member:
		:param membername:
		:param isattr:
		:param parent:
		"""

		return not isinstance(parent, ModuleDocumenter) and isattr and member is INSTANCEATTR

	def import_parent(self) -> Any:
		"""
		Import and return the attribute's parent.
		"""

		try:
			parent = importlib.import_module(self.modname)
			for name in self.objpath[:-1]:
				parent = self.get_attr(parent, name)

			return parent
		except (ImportError, AttributeError):
			return None

	def import_object(self, raiseerror: bool = False) -> bool:
		"""
		Never import anything.
		"""

		# disguise as an attribute
		self.objtype = "attribute"
		self.object = INSTANCEATTR
		self.parent = self.import_parent()
		self._datadescriptor = False

		return True

	def add_content(self, more_content: Any, no_docstring: bool = False):
		"""
		Never try to get a docstring from the object.
		"""

		super().add_content(more_content, no_docstring=True)


def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.variables`.

	:param app: The Sphinx app.
	"""

	app.setup_extension("sphinx.ext.autodoc")
	app.add_autodocumenter(VariableDocumenter)
	app.add_autodocumenter(TypedAttributeDocumenter, override=True)
	app.add_autodocumenter(InstanceAttributeDocumenter, override=True)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

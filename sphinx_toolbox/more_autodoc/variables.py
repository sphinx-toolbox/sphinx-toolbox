#!/usr/bin/env python3
#
#  variables.py
r"""
Documenter for module level variables, similar to :rst:dir:`autodata` but
with a different appearance and more customisation options.

.. versionadded:: 0.6.0
.. extensions:: sphinx_toolbox.more_autodoc.variables
.. versionchanged:: 0.7.0  Added ``*AttributeDocumenter``\s
.. versionchanged:: 1.1.0  Added :class:`~.SlotsAttributeDocumenter`


Usage
----------

.. rst:directive:: autovariable

	Directive to automatically document a variable.

	The output is based on the :rst:dir:`autodata` directive, and takes all of its options,
	plus these additional ones:

	.. rst:directive:option:: no-value

		Don't show the value of the variable.

	.. rst:directive:option:: value: value
		:type: string

		Show this instead of the value taken from the Python source code.

	.. rst:directive:option:: no-type

		Don't show the type of the variable.

	.. rst:directive:option:: type: type
		:type: string

		Show this instead of the type taken from the Python source code.

	An example of the output cen be seen below for :py:obj:`~.type_template`.

API Reference
----------------
"""  # noqa: D400
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

# stdlib
import importlib
import sys
import warnings
from contextlib import suppress
from typing import Any, List, Optional, cast, get_type_hints

# 3rd party
import sphinx
from sphinx.application import Sphinx
from sphinx.deprecation import RemovedInSphinx50Warning
from sphinx.errors import PycodeError
from sphinx.ext.autodoc import (
		INSTANCEATTR,
		SLOTSATTR,
		UNINITIALIZED_ATTR,
		ClassLevelDocumenter,
		DocstringStripSignatureMixin,
		Documenter,
		ModuleDocumenter,
		ModuleLevelDocumenter,
		Options,
		annotation_option,
		import_object,
		logger,
		mock
		)
from sphinx.ext.autodoc.directive import DocumenterBridge
from sphinx.pycode import ModuleAnalyzer
from sphinx.util import inspect
from sphinx.util.docstrings import prepare_docstring
from sphinx.util.inspect import ForwardRef, object_description, safe_getattr

# this package
from sphinx_toolbox._data_documenter import DataDocumenter
from sphinx_toolbox.more_autodoc.typehints import format_annotation
from sphinx_toolbox.utils import SphinxExtMetadata, add_nbsp_substitution, flag, metadata_add_version

__all__ = [
		"VariableDocumenter",
		"TypedAttributeDocumenter",
		"InstanceAttributeDocumenter",
		"SlotsAttributeDocumenter",
		"type_template",
		"get_variable_type",
		"setup",
		]


def get_variable_type(documenter: Documenter) -> str:
	"""
	Returns the formatted type annotation for a variable.

	:param documenter:
	"""

	try:
		annotations = get_type_hints(documenter.parent)
	except NameError:
		# Failed to evaluate ForwardRef (maybe TYPE_CHECKING)
		annotations = safe_getattr(documenter.parent, "__annotations__", {})
	except (TypeError, KeyError, AttributeError):
		# KeyError: a broken class found (refs: https://github.com/sphinx-doc/sphinx/issues/8084)
		# AttributeError is raised on 3.5.2 (fixed by 3.5.3)
		annotations = {}

	if documenter.objpath[-1] in annotations:
		ann = annotations.get(documenter.objpath[-1])

		if isinstance(ann, str):
			return format_annotation(ann.strip("'\""))

		return format_annotation(ann)
	else:
		# Instance attribute
		key = ('.'.join(documenter.objpath[:-1]), documenter.objpath[-1])

		if documenter.analyzer and key in documenter.analyzer.annotations:
			# Forward references will have quotes
			annotation: str = documenter.analyzer.annotations[key].strip("'\"")

			try:
				module_dict = sys.modules[documenter.parent.__module__].__dict__

				if annotation.isidentifier() and annotation in module_dict:
					return format_annotation(module_dict[annotation])
				else:
					ref = ForwardRef(annotation)
					if sys.version_info < (3, 9):
						evaled = ref._evaluate(module_dict, module_dict)
					else:
						evaled = ref._evaluate(module_dict, module_dict, set())

					return format_annotation(evaled)

			except (NameError, TypeError, ValueError, AttributeError):
				return annotation
		else:
			return ''


type_template = "   **Type:** |nbsp| |nbsp| |nbsp| |nbsp| %s"
"""
Template for rendering type annotations in :class:`~.VariableDocumenter`,
:class:`~.TypedAttributeDocumenter` and :class:`~.InstanceAttributeDocumenter`.

Renders like:

	**Type:** |nbsp| |nbsp| |nbsp| |nbsp| :class:`str`

.. note::

	Be sure to call :func:~.add_nbsp_substitution` in the ``setup`` function
	of any extensions using this template.
"""


class VariableDocumenter(DataDocumenter):
	"""
	Specialized Documenter subclass for data items.
	"""

	directivetype = "data"
	objtype = "variable"
	priority: float = DataDocumenter.priority + 0.5  # type: ignore  # keeps it below TypeVarDocumenter
	option_spec = {
			"no-value": flag,
			"no-type": flag,
			"type": str,
			"value": str,
			**DataDocumenter.option_spec,
			}

	def __init__(self, directive: DocumenterBridge, name: str, indent: str = '') -> None:
		super().__init__(directive=directive, name=name, indent=indent)
		self.options = Options(self.options.copy())
		add_nbsp_substitution(self.env.app.config)

	def add_directive_header(self, sig: str):
		"""
		Add the directive's header.

		:param sig:
		"""

		sourcename = self.get_sourcename()

		no_value = self.options.get("no-value", False)
		no_type = self.options.get("no-type", False)

		if not self.options.get("annotation", ''):
			ModuleLevelDocumenter.add_directive_header(self, sig)

			if not no_value:
				if "value" in self.options:
					self.add_line(f"   :value: {self.options['value']}", sourcename)
				else:
					with suppress(ValueError):
						if self.object is not UNINITIALIZED_ATTR:
							objrepr = object_description(self.object)
							self.add_line(f"   :value: {objrepr}", sourcename)

			self.add_line('', sourcename)

			if not no_type:
				if "type" in self.options:
					the_type = self.options["type"]
				else:
					# obtain type annotation for this data
					the_type = get_variable_type(self)
					if not the_type.strip():
						obj_type = type(self.object)

						if obj_type is object:
							return

						try:
							the_type = format_annotation(obj_type)
						except Exception:
							return

				line = type_template % the_type
				self.add_line(line, sourcename)

		else:
			super().add_directive_header(sig)


class TypedAttributeDocumenter(DocstringStripSignatureMixin, ClassLevelDocumenter):
	"""
	Alternative version of :class:`sphinx.ext.autodoc.AttributeDocumenter`
	with better type hint rendering.

	Specialized Documenter subclass for attributes.

	.. versionadded:: 0.7.0
	.. versionchanged:: 1.0.0  Now uses the type of the variable if it is not explicitly annotated.
	"""  # noqa: D400

	objtype = "attribute"
	member_order = 60
	option_spec = dict(ModuleLevelDocumenter.option_spec)
	option_spec["annotation"] = annotation_option

	# must be higher than the MethodDocumenter, else it will recognize
	# some non-data descriptors as methods
	priority = 10

	def __init__(self, directive: DocumenterBridge, name: str, indent: str = '') -> None:
		super().__init__(directive=directive, name=name, indent=indent)
		self.options = Options(self.options.copy())
		self._datadescriptor = True

	@staticmethod
	def is_function_or_method(obj: Any) -> bool:  # noqa: D102
		return inspect.isfunction(obj) or inspect.isbuiltin(obj) or inspect.ismethod(obj)

	@classmethod
	def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
		"""
		Called to see if a member can be documented by this documenter.
		"""

		if inspect.isattributedescriptor(member):
			return True
		elif (
				not isinstance(parent, ModuleDocumenter) and not inspect.isroutine(member)
				and not isinstance(member, type)
				):
			return True
		else:
			return False

	def document_members(self, all_members: bool = False) -> None:  # noqa: D102
		pass

	def isinstanceattribute(self) -> bool:
		"""
		Check the subject is an instance attribute.
		"""

		try:
			analyzer = ModuleAnalyzer.for_module(self.modname)
			attr_docs = analyzer.find_attr_docs()
			if self.objpath:
				key = ('.'.join(self.objpath[:-1]), self.objpath[-1])
				if key in attr_docs:
					return True

			return False
		except PycodeError:
			return False

	def import_object(self, raiseerror: bool = False) -> bool:
		"""
		Import the object given by *self.modname* and *self.objpath* and set it as ``self.object``.

		:returns: :py:obj:`True` if successful, :py:obj:`False` if an error occurred.
		"""

		try:
			ret = super().import_object(raiseerror=True)
			if inspect.isenumattribute(self.object):
				self.object = self.object.value
			if inspect.isattributedescriptor(self.object):
				self._datadescriptor = True
			else:
				# if it's not a data descriptor
				self._datadescriptor = False
		except ImportError as exc:
			if self.isinstanceattribute():
				self.object = INSTANCEATTR
				self._datadescriptor = False
				ret = True
			elif raiseerror:
				raise
			else:
				logger.warning(exc.args[0], type="autodoc", subtype="import_object")
				self.env.note_reread()
				ret = False

		return ret

	def get_real_modname(self) -> str:
		"""
		Get the real module name of an object to document.

		It can differ from the name of the module through which the object was imported.
		"""

		return self.get_attr(self.parent or self.object, "__module__", None) or self.modname

	def add_directive_header(self, sig: str):
		"""
		Add the directive's header.

		:param sig:
		"""

		sourcename = self.get_sourcename()

		no_value = self.options.get("no-value", False)
		no_type = self.options.get("no-type", False)

		if not self.options.get("annotation", ''):
			ClassLevelDocumenter.add_directive_header(self, sig)

			# data descriptors do not have useful values
			if not no_value and not self._datadescriptor:
				if "value" in self.options:
					self.add_line("   :value: " + self.options["value"], sourcename)
				else:
					with suppress(ValueError):
						if self.object is not INSTANCEATTR:
							objrepr = object_description(self.object)
							self.add_line("   :value: " + objrepr, sourcename)

			self.add_line('', sourcename)

			if not no_type:
				if "type" in self.options:
					self.add_line(type_template % self.options["type"], sourcename)
				else:
					# obtain type annotation for this attribute
					the_type = get_variable_type(self)
					if not the_type.strip():
						obj_type = type(self.object)

						if obj_type is object:
							return

						try:
							the_type = format_annotation(obj_type)
						except Exception:
							return

					line = type_template % the_type
					self.add_line(line, sourcename)

		else:
			super().add_directive_header(sig)

	def get_doc(  # type: ignore
			self,
			encoding: Optional[str] = None,
			ignore: Optional[int] = None,
			) -> List[List[str]]:
		"""
		Decode and return lines of the docstring(s) for the object.

		:param encoding:
		:param ignore:
		"""

		try:
			# Disable `autodoc_inherit_docstring` temporarily to avoid to obtain
			# a docstring from the value which descriptor returns unexpectedly.
			# ref: https://github.com/sphinx-doc/sphinx/issues/7805
			orig = self.env.config.autodoc_inherit_docstrings
			self.env.config.autodoc_inherit_docstrings = False  # type: ignore

			# Sphinx's signature is wrong wrt Optional
			if sphinx.version_info >= (4, 0):
				if encoding is not None:
					raise TypeError("The 'encoding' argument to get_doc was removed in Sphinx 4")
				else:
					return super().get_doc(ignore=cast(int, ignore)) or []
			else:
				return super().get_doc(cast(str, encoding), cast(int, ignore)) or []  # type: ignore
		finally:
			self.env.config.autodoc_inherit_docstrings = orig  # type: ignore

	def add_content(self, more_content: Any, no_docstring: bool = False) -> None:
		"""
		Add content from docstrings, attribute documentation and user.
		"""

		with warnings.catch_warnings():
			# TODO: work out what to do about this
			warnings.simplefilter("ignore", RemovedInSphinx50Warning)

			if not self._datadescriptor:
				# if it's not a data descriptor, its docstring is very probably the
				# wrong thing to display
				no_docstring = True
			super().add_content(more_content, no_docstring)


class InstanceAttributeDocumenter(TypedAttributeDocumenter):
	"""
	Alternative version of :class:`sphinx.ext.autodoc.InstanceAttributeDocumenter`
	with better type hint rendering.

	Specialized Documenter subclass for attributes that cannot be imported
	because they are instance attributes (e.g. assigned in ``__init__``).

	.. versionadded:: 0.7.0
	.. versionchanged:: 1.0.0  Now uses the type of the variable if it is not explicitly annotated.
	"""  # noqa: D400

	objtype = "instanceattribute"
	directivetype = "attribute"
	member_order = 60

	# must be higher than TypedAttributeDocumenter
	priority = 11

	@classmethod
	def can_document_member(
			cls,
			member: Any,
			membername: str,
			isattr: bool,
			parent: Any,
			) -> bool:
		"""
		Called to see if a member can be documented by this documenter.

		This documenter only documents INSTANCEATTR members.

		:param member: The member being checked.
		:param membername: The name of the member.
		:param isattr:
		:param parent: The parent of the member.
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

		:param raiseerror:
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


class SlotsAttributeDocumenter(TypedAttributeDocumenter):
	r"""
	Alternative version of :class:`sphinx.ext.autodoc.InstanceAttributeDocumenter`
	with better type hint rendering.

	Specialized Documenter subclass for attributes that cannot be imported
	because they are attributes in __slots__.

	.. versionadded:: 1.1.0

	.. latex:vspace:: 10px

	"""  # noqa: D400

	objtype = "slotsattribute"
	directivetype = "attribute"
	member_order = 60

	# must be higher than AttributeDocumenter
	priority = 11

	@classmethod
	def can_document_member(
			cls,
			member: Any,
			membername: str,
			isattr: bool,
			parent: Any,
			) -> bool:
		"""
		Called to see if a member can be documented by this documenter.

		This documenter only documents SLOTSATTR members.

		:param member: The member being checked.
		:param membername: The name of the member.
		:param isattr:
		:param parent: The parent of the member.
		"""

		return member is SLOTSATTR

	def import_object(self, raiseerror: bool = False) -> bool:
		"""
		Never import anything.

		:param raiseerror:
		"""

		# disguise as an attribute
		self.objtype = "attribute"
		self._datadescriptor = True

		with mock(self.env.config.autodoc_mock_imports):
			try:
				ret = import_object(
						self.modname,
						self.objpath[:-1],
						"class",
						attrgetter=self.get_attr,
						warningiserror=self.env.config.autodoc_warningiserror
						)
				self.module, _, _, self.parent = ret
				return True
			except ImportError as exc:
				if raiseerror:
					raise
				else:
					logger.warning(exc.args[0], type="autodoc", subtype="import_object")
					self.env.note_reread()
					return False

	def get_doc(  # type: ignore
			self,
			encoding: Optional[str] = None,
			ignore: Optional[int] = None,
			) -> List[List[str]]:
		"""
		Decode and return lines of the docstring(s) for the object.

		:param encoding:
		:param ignore:
		"""

		if ignore is not None:  # pragma: no cover
			warnings.warn(
					"The 'ignore' argument to autodoc.%s.get_doc() is deprecated." % self.__class__.__name__,
					RemovedInSphinx50Warning,
					stacklevel=2
					)

		name = self.objpath[-1]
		__slots__ = safe_getattr(self.parent, "__slots__", [])

		if isinstance(__slots__, dict) and isinstance(__slots__.get(name), str):
			return [prepare_docstring(__slots__[name])]
		else:
			return []


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.variables`.

	:param app: The Sphinx application.
	"""

	app.setup_extension("sphinx.ext.autodoc")
	app.setup_extension("sphinx_toolbox.more_autosummary")

	app.add_autodocumenter(VariableDocumenter)
	app.add_autodocumenter(TypedAttributeDocumenter, override=True)
	app.add_autodocumenter(InstanceAttributeDocumenter, override=True)
	app.add_autodocumenter(SlotsAttributeDocumenter, override=True)

	app.connect("config-inited", lambda _, config: add_nbsp_substitution(config))

	return {"parallel_read_safe": True}

#!/usr/bin/env python3
#
#  typevars.py
r"""
Documenter for module level :class:`typing.TypeVar`\'s, similar to Sphinx's
``autotypevar`` but with a different appearance.

.. versionadded:: 1.3.0
.. extensions:: sphinx_toolbox.more_autodoc.typevars

.. latex:vspace:: -15px

Configuration
-------------

.. confval:: all_typevars
	:type: :class:`bool`
	:default: False

	Document all :class:`typing.TypeVar`\s, even if they have no docstring.


.. confval:: no_unbound_typevars
	:type: :class:`bool`
	:default: True

	Only document :class:`typing.TypeVar`\s that have a constraint of are bound.

	This option has no effect if :confval:`all_typevars` is False.


.. latex:vspace:: -15px

Usage
----------

.. latex:vspace:: -10px

.. rst:directive:: autotypevar

	Directive to automatically document a :class:`typing.TypeVar`.

	The output is based on the :rst:dir:`autodata` directive, and takes all of its options
	plus these additional ones:

	.. rst:directive:option:: no-value

		Don't show the value of the variable.

	.. rst:directive:option:: value: value
		:type: string

		Show this instead of the value taken from the Python source code.

	.. rst:directive:option:: no-type

		Don't show the type of the variable.


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
import sys
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union

# 3rd party
from domdf_python_tools.words import word_join
from sphinx.application import Sphinx
from typing_extensions import Protocol

# this package
from sphinx_toolbox._data_documenter import DataDocumenter
from sphinx_toolbox.config import ToolboxConfig
from sphinx_toolbox.more_autodoc.typehints import ForwardRef, format_annotation
from sphinx_toolbox.more_autodoc.variables import VariableDocumenter
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = [
		"TypeVarDocumenter",
		"unskip_typevars",
		"setup",
		]


class TypeVarDocumenter(VariableDocumenter):
	r"""
	Alternative version of :class:`sphinx.ext.autodoc.TypeVarDocumenter`
	with better type hint rendering.

	Specialized Documenter subclass for :class:`typing.TypeVar`\s.
	"""  # noqa: D400

	objtype = "typevar"
	directivetype = "data"
	priority = DataDocumenter.priority + 1

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

		:param member: The member being checked.
		:param membername: The name of the member.
		:param isattr:
		:param parent: The parent of the member.
		"""

		return isinstance(member, TypeVar)

	def resolve_type(self, forward_ref: ForwardRef) -> Type:
		"""
		Resolve a :class:`typing.ForwardRef` using the module the :class:`~typing.TypeVar` belongs to.

		:param forward_ref:
		"""

		if forward_ref.__forward_evaluated__:
			return forward_ref.__forward_value__
		else:
			if sys.version_info[:2] == (3, 6) and self.object.__module__ == "typing" and isinstance(
					self.parent, ModuleType
					):
				# __module__ is 'typing' for 3.6
				globanls = self.parent.__dict__
			else:
				globanls = sys.modules[self.object.__module__].__dict__

			eval_ = eval
			return eval_(forward_ref.__forward_code__, globanls, globanls)

	def add_content(self, more_content: Any, no_docstring: bool = False) -> None:
		"""
		Add content from docstrings, attribute documentation and user.

		:param more_content:
		:param no_docstring:
		"""

		obj: _TypeVar = self.object
		sourcename = self.get_sourcename()
		constraints = [self.resolve_type(c) if isinstance(c, ForwardRef) else c for c in obj.__constraints__]
		description = []

		bound_to: Optional[Type]

		if isinstance(obj.__bound__, ForwardRef):
			bound_to = self.resolve_type(obj.__bound__)
		else:
			bound_to = obj.__bound__

		if obj.__covariant__:
			description.append("Covariant")
		elif obj.__contravariant__:
			description.append("Contravariant")
		else:
			description.append("Invariant")

		description.append(":class:`~typing.TypeVar`")

		if constraints:
			description.append("constrained to")
			description.append(word_join(format_annotation(c, fully_qualified=True) for c in constraints))
		elif bound_to:
			description.append("bound to")
			description.append(format_annotation(bound_to, fully_qualified=True))

		# if self.analyzer:
		# 	attr_docs = self.analyzer.find_attr_docs()
		# 	if self.objpath:
		# 		key = ('.'.join(self.objpath[:-1]), self.objpath[-1])
		# 		if key in attr_docs:
		# 			return

		self.add_line('', sourcename)
		self.add_line(' '.join(description).rstrip() + '.', sourcename)  # "   " +
		self.add_line('', sourcename)

		super().add_content(more_content, no_docstring)

	def add_directive_header(self, sig: str) -> None:
		"""
		Add the directive's header.

		:param sig:
		"""

		obj: _TypeVar = self.object
		sourcename = self.get_sourcename()
		constraints = [self.resolve_type(c) if isinstance(c, ForwardRef) else c for c in obj.__constraints__]
		sig_elements = [obj.__name__, *(c.__name__ for c in constraints)]

		bound_to: Optional[Type]

		if isinstance(obj.__bound__, ForwardRef):
			bound_to = self.resolve_type(obj.__bound__)
		else:
			bound_to = obj.__bound__

		if bound_to is not None:
			try:
				sig_elements.append(f"bound={bound_to.__name__}")
			except AttributeError:
				sig_elements.append(f"bound={repr(bound_to)}")

		if obj.__covariant__:
			sig_elements.append(f"covariant=True")
		elif obj.__contravariant__:
			sig_elements.append(f"contravariant=True")

		self.options["value"] = f"TypeVar({', '.join(sig_elements)})"
		self.add_line('', sourcename)

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

		if self.object.__doc__ != TypeVar.__doc__:
			return super().get_doc() or []
		else:
			return []


def validate_config(app: Sphinx, config: ToolboxConfig):
	r"""
	Validate the provided configuration values.

	See :class:`~sphinx_toolbox.config.ToolboxConfig` for a list of the configuration values.

	:param app: The Sphinx application.
	:param config:
	:type config: :class:`~sphinx.config.Config`
	"""

	if config.all_typevars:
		app.connect("autodoc-skip-member", unskip_typevars)


def unskip_typevars(
		app: Sphinx,
		what: str,
		name: str,
		obj: Any,
		skip: bool,
		options: Dict[str, Any],
		) -> Optional[bool]:
	r"""
	Unskip undocumented :class:`typing.TypeVar`\s if :confval:`all_typevars` is :py:obj:`True`.

	:param app: The Sphinx application.
	:param what: The type of the object which the docstring belongs to (one of
		``'module'``, ``'class'``, ``'exception'``, ``'function'``, ``'method'``,
		``'attribute'``).
	:param name: The fully qualified name of the object.
	:param obj: The object itself.
	:param skip: A boolean indicating if autodoc will skip this member if the
		user handler does not override the decision.
	:param options: The options given to the directive: an object with attributes
		``inherited_members``, ``undoc_members``, ``show_inheritance`` and
		``noindex`` that are true if the flag option of same name was given to the
		auto directive.
	"""

	assert app.env is not None

	if isinstance(obj, TypeVar):
		if app.env.config.no_unbound_typevars:
			if obj.__bound__ or obj.__constraints__:
				return False
			else:
				return True
		else:
			return False

	return None


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.typevars`.

	:param app: The Sphinx application.
	"""

	app.setup_extension("sphinx.ext.autodoc")
	app.add_autodocumenter(TypeVarDocumenter, override=True)
	app.add_config_value("all_typevars", False, "env", types=[bool])
	app.add_config_value("no_unbound_typevars", True, "env", types=[bool])

	app.connect("config-inited", validate_config, priority=850)

	return {"parallel_read_safe": True}


class _TypeVar(Protocol):
	if sys.version_info < (3, 7):  # pragma: no cover (<py37)
		__constraints__: Tuple[Any, ...]
		__bound__: Union[Type, Any, None]
	else:  # pragma: no cover (py37+)
		__constraints__: Tuple[Union[Type, ForwardRef], ...]
		__bound__: Union[Type, ForwardRef, None]

	__covariant__: bool
	__contravariant__: bool
	__name__: str

#!/usr/bin/env python3
#
#  overloads.py
r"""
Documenters for functions and methods which display overloads differently.

.. versionadded:: 1.4.0


Configuration
----------------

.. confval:: overloads_location
	:type: :class:`str`
	:default: ``'signature'``

	The location to display overloads at:

	* ``'signature'`` -- Display overloads above the function signature.
	* ``'top'`` -- Display overloads at the top of the docstring, immediately below the signature.
	* ``'bottom'`` -- Display overloads at the bottom of the docstring, or immediately below the return type.


API Reference
----------------
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
from inspect import Parameter, Signature
from typing import TYPE_CHECKING, Any, Dict, List

# 3rd party
from domdf_python_tools.stringlist import StringList
from sphinx.application import Sphinx
from sphinx.ext import autodoc
from sphinx.util import inspect
from sphinx.util.inspect import evaluate_signature, safe_getattr, stringify_signature

# this package
from sphinx_toolbox.more_autodoc.typehints import default_preprocessors, format_annotation
from sphinx_toolbox.utils import SphinxExtMetadata

__all__ = [
		"OverloadMixin",
		"FunctionDocumenter",
		"MethodDocumenter",
		"setup",
		]

if TYPE_CHECKING:
	_OverloadMixinBase = autodoc.ModuleLevelDocumenter
else:
	_OverloadMixinBase = object


class OverloadMixin(_OverloadMixinBase):
	"""
	Mixin class for function and class documenters that changes the appearance of overloaded functions.

	.. versionadded:: 1.4.0
	"""

	def create_body_overloads(self) -> StringList:
		"""
		Create the overloaded implementations for insertion into to the body of the documenter's output.
		"""

		output = StringList()
		formatted_overloads = []

		output.blankline()
		# output.append(":Overloaded Implementations:")
		output.append(":Overloads:")
		output.blankline()

		# Size varies depending on docutils config
		output.indent_type = " "
		output.indent_size = self.env.app.config.docutils_tab_width  # type: ignore

		if self.analyzer and '.'.join(self.objpath) in self.analyzer.overloads:

			for overload in self.analyzer.overloads.get('.'.join(self.objpath)):  # type: ignore
				overload = self.process_overload_signature(overload)

				buf = [format_annotation(self.object), r"\("]

				for name, param in overload.parameters.items():
					buf.append(f"**{name}**")
					if param.annotation is not Parameter.empty:
						buf.append(r"\: ")
						buf.append(format_annotation(param.annotation))
					if param.default is not Parameter.empty:
						buf.append(" = ")
						buf.append(param.default)
					buf.append(r"\, ")

				if buf[-2][-1] != '`':
					buf[-1] = r" )"
				else:
					buf[-1] = r")"

				if overload.return_annotation is not Parameter.empty:
					buf.append(" -> ")
					buf.append(format_annotation(overload.return_annotation))

				formatted_overloads.append(''.join(buf))

			if len(formatted_overloads) == 1:
				output.append(formatted_overloads[0])
			else:
				for line in formatted_overloads:
					output.append(f"* {line}")
					output.blankline(ensure_single=True)

			return output

		return StringList()

	def process_overload_signature(self, overload: Signature) -> Signature:
		"""
		Processes the signature of the given overloaded implementation.

		:param overload:
		"""

		parameters = []
		non_overload_sig = inspect.signature(self.object)

		for param, non_overload_param in zip(overload.parameters.values(), non_overload_sig.parameters.values()):
			default = param.default

			if default is not Parameter.empty:
				for check, preprocessor in default_preprocessors:
					if check(default):
						default = preprocessor(default)
						break

			if param.annotation is non_overload_param.annotation:
				annotation = Parameter.empty
			else:
				annotation = param.annotation
			parameters.append(param.replace(default=default, annotation=annotation))

		if non_overload_sig.return_annotation is overload.return_annotation:
			overload = overload.replace(parameters=parameters, return_annotation=Parameter.empty)
		else:
			overload = overload.replace(parameters=parameters)

		return overload

	def add_content(self, more_content: Any, no_docstring: bool = False) -> None:
		"""
		Add content from docstrings, attribute documentation and the user.

		:param more_content:
		:param no_docstring:
		"""

		if self.env.config.overloads_location == "bottom":

			insert_index = -1

			def process_docstring(
					app: Sphinx,
					what: str,
					name: str,
					obj: Any,
					options: Dict[str, Any],
					lines: List[str],
					) -> None:

				nonlocal insert_index

				if callable(obj):
					for i, line in enumerate(lines):
						if line.startswith(":rtype:"):
							insert_index = i - len(lines) + 1
							break

						elif line.startswith(":return:") or line.startswith(":returns:"):
							insert_index = i - len(lines)

			listener_id = self.env.app.connect("autodoc-process-docstring", process_docstring, priority=300)
			super().add_content(more_content, no_docstring)
			self.env.app.disconnect(listener_id)

			for line in self.create_body_overloads():
				self.directive.result.insert(insert_index, f"{self.indent}{line}", self.get_sourcename())

		else:
			super().add_content(more_content, no_docstring)


class FunctionDocumenter(OverloadMixin, autodoc.FunctionDocumenter):
	"""
	Custom :class:`sphinx.ext.autodoc.FunctionDocumenter` which
	renders overloads differently.

	.. versionadded:: 1.4.0
	"""  # noqa: D400

	def format_signature(self, **kwargs: Any) -> str:
		"""
		Format the function's signature, including those for any overloaded implementations.

		:param kwargs:

		:return: The signature(s), as a multi-line string.
		"""

		sigs = []

		if self.analyzer and '.'.join(self.objpath) in self.analyzer.overloads:
			overloaded = True
		else:
			overloaded = False
			sig = super(autodoc.FunctionDocumenter, self).format_signature(**kwargs)
			sigs.append(sig)

		if inspect.is_singledispatch_function(self.object):
			# append signature of singledispatch'ed functions
			for typ, func in self.object.registry.items():
				if typ is object:
					pass  # default implementation. skipped.
				else:
					self.annotate_to_first_argument(func, typ)

					documenter = FunctionDocumenter(self.directive, '')
					documenter.object = func
					documenter.objpath = [None]  # type: ignore
					sigs.append(documenter.format_signature())

		if overloaded:
			if self.env.config.overloads_location == "signature":
				for overload in self.analyzer.overloads.get('.'.join(self.objpath)):  # type: ignore
					sig = stringify_signature(self.process_overload_signature(overload), **kwargs)
					sigs.append(sig)

			sig = super(autodoc.FunctionDocumenter, self).format_signature(**kwargs)
			sigs.append(sig)

		return "\n".join(sigs)

	def add_directive_header(self, sig: str) -> None:
		"""
		Add the directive's header.

		:param sig:
		"""

		super().add_directive_header(sig)

		if self.env.config.overloads_location == "top":
			for line in self.create_body_overloads():
				self.add_line(f"{self.content_indent}{line}", self.get_sourcename())

	def process_overload_signature(self, overload: Signature) -> Signature:
		"""
		Processes the signature of the given overloaded implementation.

		:param overload:
		"""

		__globals__ = safe_getattr(self.object, "__globals__", {})
		overload = evaluate_signature(overload, __globals__)
		return super().process_overload_signature(overload)


class MethodDocumenter(OverloadMixin, autodoc.MethodDocumenter):
	"""
	Custom :class:`sphinx.ext.autodoc.MethodDocumenter` which
	renders overloads differently.

	.. versionadded:: 1.4.0
	"""  # noqa: D400

	def format_signature(self, **kwargs: Any) -> str:
		"""
		Format the method's signature, including those for any overloaded implementations.

		:param kwargs:

		:return: The signature(s), as a multi-line string.
		"""

		sigs = []

		if self.analyzer and '.'.join(self.objpath) in self.analyzer.overloads:
			overloaded = True
		else:
			overloaded = False
			sig = super(autodoc.MethodDocumenter, self).format_signature(**kwargs)
			sigs.append(sig)

		meth = self.parent.__dict__.get(self.objpath[-1])
		if inspect.is_singledispatch_method(meth):
			# append signature of singledispatch'ed functions
			for typ, func in meth.dispatcher.registry.items():
				if typ is object:
					pass  # default implementation. skipped.
				else:
					self.annotate_to_first_argument(func, typ)

					documenter = MethodDocumenter(self.directive, '')
					documenter.parent = self.parent
					documenter.object = func
					documenter.objpath = [None]  # type: ignore
					sigs.append(documenter.format_signature())

		if overloaded:
			if self.env.config.overloads_location == "signature":
				for overload in self.analyzer.overloads.get('.'.join(self.objpath)):  # type: ignore
					sig = stringify_signature(self.process_overload_signature(overload), **kwargs)
					sigs.append(sig)

			sig = super(autodoc.MethodDocumenter, self).format_signature(**kwargs)
			sigs.append(sig)

		return "\n".join(sigs)

	def add_directive_header(self, sig: str) -> None:
		"""
		Add the directive's header.

		:param sig:
		"""

		super().add_directive_header(sig)

		if self.env.config.overloads_location == "top":
			for line in self.create_body_overloads():
				self.add_line(f"{self.content_indent}{line}", self.get_sourcename())

	def process_overload_signature(self, overload: Signature) -> Signature:
		"""
		Processes the signature of the given overloaded implementation.

		:param overload:
		"""

		__globals__ = safe_getattr(self.object, "__globals__", {})
		overload = evaluate_signature(overload, __globals__)

		if not inspect.isstaticmethod(self.object, cls=self.parent, name=self.object_name):
			overload = overload.replace(parameters=list(overload.parameters.values())[1:])

		return super().process_overload_signature(overload)


def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.overloads`.

	:param app: The Sphinx app.

	.. versionadded:: 1.4.0
	"""

	# this package
	from sphinx_toolbox import __version__

	app.add_autodocumenter(FunctionDocumenter, override=True)
	app.add_autodocumenter(MethodDocumenter, override=True)
	app.add_config_value("overloads_location", "signature", "env")  # top (of body), bottom (of body)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

#!/usr/bin/env python3
#
#  autodoc_typehints.py
"""
| Enhanced version of `sphinx-autodoc-typehints <https://pypi.org/project/sphinx-autodoc-typehints/>`_.
| Copyright (c) Alex Grönholm

The changes are:

* *None* is formatted as :py:obj:`None` and not ``None``.
  If `intersphinx <https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html>`_
  is used this will be a link to the Python documentation.

* If the signature of the object cannot be read, the signature provided by Sphinx will be used
  rather than raising an error. This usually occurs for methods of builtin types.

* :class:`typing.TypeVar`\\s are linked to if they have been included in the documentation.

* If a function/method argument has a :class:`module <types.ModuleType>` object as its default
  value a better representation will be shown in the signature.

  For example:

	.. autofunction:: sphinx_toolbox.autodoc_typehints.serialise
		:noindex:

  Previously this would have shown the full path to the source file. Now it displays ``<module 'json'>``.
"""
#
#  Copyright (c) Alex Grönholm
#  Changes copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# stdlib
import inspect
import json
from types import ModuleType
from typing import Any, AnyStr, Dict, Optional, Tuple, TypeVar

# 3rd party
import sphinx_autodoc_typehints  # type: ignore
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError
from sphinx.util.inspect import signature as Signature
from sphinx.util.inspect import stringify_signature
from sphinx_toolbox import __version__

__all__ = [
		"Module",
		"get_annotation_module",
		"get_annotation_class_name",
		"get_annotation_args",
		"format_annotation",
		"process_signature",
		"get_all_type_hints",
		"backfill_type_hints",
		"load_args",
		"split_type_comment_args",
		"process_docstring",
		"builder_ready",
		]


get_annotation_module = sphinx_autodoc_typehints.get_annotation_module
get_annotation_class_name = sphinx_autodoc_typehints.get_annotation_class_name
get_annotation_args = sphinx_autodoc_typehints.get_annotation_args
get_all_type_hints = sphinx_autodoc_typehints.get_all_type_hints
backfill_type_hints = sphinx_autodoc_typehints.backfill_type_hints
load_args = sphinx_autodoc_typehints.load_args
split_type_comment_args = sphinx_autodoc_typehints.split_type_comment_args
process_docstring = sphinx_autodoc_typehints.process_docstring
builder_ready = sphinx_autodoc_typehints.builder_ready


# Demonstration of module default argument in signature
def serialise(obj: Any, library=json) -> str:
	"""
	Serialise an object into a JSON string.

	:param obj: The object to serialise.
	:param library: The JSON library to use.
	:no-default library:

	:return: The JSON string.
	"""


class Module:
	"""
	Used to represent a module in a Sphinx function/class signature.

	:param name: The name of the module.
	"""

	def __init__(self, name: str):
		self.name: str = name

	def __repr__(self) -> str:
		"""
		Returns a string representation of the :class:`~.Module`.
		"""

		return f"<module {self.name!r}>"


def format_annotation(annotation, fully_qualified: bool = False) -> str:
	"""
	Format a type annotation.

	:param annotation:
	:param fully_qualified:

	:return:
	"""

	# Special cases
	if annotation is None or annotation is type(None):  # noqa: E721
		return ':py:obj:`None`'
	elif annotation is Ellipsis:
		return '...'

	# Type variables are also handled specially
	try:
		if isinstance(annotation, TypeVar) and annotation is not AnyStr:  # type: ignore
			return f'\\:py:data:`{annotation!r}`'
	except TypeError:
		pass

	try:
		module = sphinx_autodoc_typehints.get_annotation_module(annotation)
		class_name = sphinx_autodoc_typehints.get_annotation_class_name(annotation, module)
		args = sphinx_autodoc_typehints.get_annotation_args(annotation, module, class_name)
	except ValueError:
		return str(annotation)

	# Redirect all typing_extensions types to the stdlib typing module
	if module == 'typing_extensions':
		module = 'typing'

	full_name = (module + '.' + class_name) if module != 'builtins' else class_name
	prefix = '' if fully_qualified or full_name == class_name else '~'
	role = 'data' if class_name in sphinx_autodoc_typehints.pydata_annotations else 'class'
	args_format = '\\[{}]'
	formatted_args = ''

	# Some types require special handling
	if full_name == 'typing.NewType':
		args_format = f'\\(:py:data:`~{annotation.__name__}`, {{}})'
		role = 'func'
	elif full_name == 'typing.Union' and len(args) == 2 and type(None) in args:
		full_name = 'typing.Optional'
		args = tuple(x for x in args if x is not type(None))  # noqa: E721
	elif full_name == 'typing.Callable' and args and args[0] is not ...:
		formatted_args = '\\[\\[' + ', '.join(format_annotation(arg) for arg in args[:-1]) + ']'
		formatted_args += ', ' + format_annotation(args[-1]) + ']'
	elif full_name == 'typing.Literal':
		formatted_args = '\\[' + ', '.join(repr(arg) for arg in args) + ']'

	if args and not formatted_args:
		formatted_args = args_format.format(', '.join(format_annotation(arg, fully_qualified) for arg in args))

	return f':py:{role}:`{prefix}{full_name}`{formatted_args}'


def process_signature(
		app, what:
		str, name:
		str, obj,
		options,
		signature,
		return_annotation: Any,
		) -> Optional[Tuple[str, None]]:
	"""
	Process the signature for a function/method.

	:param app:
	:param what:
	:param name:
	:param obj:
	:param options:
	:param signature:
	:param return_annotation:

	:return:
	"""

	if not callable(obj):
		return None

	original_obj = obj
	if inspect.isclass(obj):
		obj = getattr(obj, '__init__', getattr(obj, '__new__', None))

	if not getattr(obj, '__annotations__', None):
		return None

	obj = inspect.unwrap(obj)

	try:
		signature = Signature(obj)
	except ValueError:
		return None

	parameters = []

	for param in signature.parameters.values():
		default = param.default

		if default is not inspect.Parameter.empty:
			if isinstance(default, ModuleType):
				default = Module(default.__name__)

		parameters.append(param.replace(annotation=inspect.Parameter.empty, default=default))

	# The generated dataclass __init__() is weird and needs the second condition
	if '<locals>' in obj.__qualname__ and not (what == 'method' and name.endswith('.__init__')):
		sphinx_autodoc_typehints.logger.warning(
				'Cannot treat a function defined as a local function: "%s"  (use @functools.wraps)', name
				)
		return None

	if parameters:
		if inspect.isclass(original_obj) or (what == 'method' and name.endswith('.__init__')):
			del parameters[0]
		elif what == 'method':
			outer = inspect.getmodule(obj)
			for clsname in obj.__qualname__.split('.')[:-1]:
				outer = getattr(outer, clsname)

			method_name = obj.__name__
			if method_name.startswith("__") and not method_name.endswith("__"):
				# If the method starts with double underscore (dunder)
				# Python applies mangling so we need to prepend the class name.
				# This doesn't happen if it always ends with double underscore.
				class_name = obj.__qualname__.split('.')[-2]
				method_name = f"_{class_name}{method_name}"

			method_object = outer.__dict__[method_name] if outer else obj
			if not isinstance(method_object, (classmethod, staticmethod)):
				del parameters[0]

	signature = signature.replace(parameters=parameters, return_annotation=inspect.Signature.empty)

	return stringify_signature(signature), None  # .replace('\\', '\\\\')


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup Sphinx Extension.

	:param app:

	:return:
	"""

	if "sphinx_autodoc_typehints" in app.extensions:
		raise ExtensionError("'sphinx_toolbox.autodoc_typehints' must be loaded before 'sphinx_autodoc_typehints.")

	sphinx_autodoc_typehints.format_annotation = format_annotation
	sphinx_autodoc_typehints.process_signature = process_signature

	app.setup_extension("sphinx_autodoc_typehints")

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

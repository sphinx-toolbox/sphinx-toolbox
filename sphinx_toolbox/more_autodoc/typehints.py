#!/usr/bin/env python3
#
#  autodoc_typehints.py
r"""
| Enhanced version of `sphinx-autodoc-typehints <https://pypi.org/project/sphinx-autodoc-typehints/>`_.
| Copyright (c) Alex Grönholm

The changes are:

* *None* is formatted as :py:obj:`None` and not ``None``.
  If `intersphinx <https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html>`_
  is used this will now be a link to the Python documentation.

  Since :pull:`154 <agronholm/sphinx-autodoc-typehints>` this feature is now available upstream.

* If the signature of the object cannot be read, the signature provided by Sphinx will be used
  rather than raising an error.

  This usually occurs for methods of builtin types.

* :class:`typing.TypeVar`\s are linked to if they have been included in the documentation.

* If a function/method argument has a :class:`module <types.ModuleType>`, :class:`class <typing.Type>`
  or :class:`function <types.FunctionType>` object as its default value a better
  representation will be shown in the signature.

  For example:

	.. autofunction:: sphinx_toolbox.more_autodoc.typehints.serialise
		:noindex:

  Previously this would have shown the full path to the source file. Now it displays ``<module 'json'>``.

* The ability to hook into the :func:`~.process_docstring` function to edit the object's properties before the
  annotations are added to the docstring.

  This is used by `attr-utils <https://attr-utils.readthedocs.io>`_
  to add annotations based on converter functions in `attrs <https://www.attrs.org>`_ classes.

  To use this, in your extension's ``setup`` function:

  .. code-block:: python

      def setup(app: Sphinx) -> Dict[str, Any]:
          from sphinx_toolbox.more_autodoc.typehints import docstring_hooks
          docstring_hooks.append((my_hook, 75))
          return {}

  ``my_hook`` is a function that takes the object being documented as its only argument
  and returns that object after modification. The ``75`` is the priority of the hook:

   * ``< 20`` runs before ``fget`` functions are extracted from properties
   * ``< 90`` runs before ``__new__`` functions are extracted from :class:`NamedTuples <typing.NamedTuple>`.
   * ``< 100`` runs before ``__init__`` functions are extracted from classes.

* Unresolved forward references are handled better.

* Many of the built in types from the :mod:`types` module are now formatted and linked to correctly.

-----

.. extensions:: sphinx_toolbox.more_autodoc.typehints


For configuration information see https://github.com/agronholm/sphinx-autodoc-typehints

In addition the following configuration value is added by this extension:

.. confval:: hide_none_rtype
	:type: :class:`bool`
	:default: :py:obj:`False`

	Hides return types of :py:obj:`None`.


.. versionadded:: 0.4.0

.. versionchanged:: 0.6.0

	Moved from :mod:`sphinx_toolbox.autodoc_typehints`.

.. versionchanged:: 0.8.0

	Added support for namedtuples.

"""  # noqa SXL001
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
import operator
import re
import sys
import types
from types import FunctionType, ModuleType
from typing import Any, AnyStr, Callable, Dict, List, Optional, Tuple, Type, TypeVar, get_type_hints

if sys.version_info[:2] == (3, 6):
	# stdlib
	from typing import _ForwardRef as ForwardRef  # type: ignore
else:
	from typing import ForwardRef

# 3rd party
import sphinx_autodoc_typehints  # type: ignore
from domdf_python_tools.typing import (
		ClassMethodDescriptorType,
		MethodDescriptorType,
		MethodWrapperType,
		WrapperDescriptorType
		)
from domdf_python_tools.utils import etc
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError
from sphinx.util.inspect import signature as Signature
from sphinx.util.inspect import stringify_signature

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.utils import SphinxExtMetadata, code_repr, escape_trailing__, is_namedtuple

try:
	# 3rd party
	import attr
except ImportError:  # pragma: no cover
	# attrs is used in a way that it is only required in situations
	# where it is available to import, so its fine to do this.
	pass

__all__ = [
		"ObjectAlias",
		"Module",
		"Function",
		"Class",
		"process_signature",
		"process_docstring",
		"format_annotation",
		"get_all_type_hints",
		"docstring_hooks",
		"setup",
		"get_annotation_module",
		"get_annotation_class_name",
		"get_annotation_args",
		"backfill_type_hints",
		"load_args",
		"split_type_comment_args",
		"builder_ready",
		"default_preprocessors",
		"Preprocessor",
		]

get_annotation_module = sphinx_autodoc_typehints.get_annotation_module
get_annotation_class_name = sphinx_autodoc_typehints.get_annotation_class_name
get_annotation_args = sphinx_autodoc_typehints.get_annotation_args
backfill_type_hints = sphinx_autodoc_typehints.backfill_type_hints
load_args = sphinx_autodoc_typehints.load_args
split_type_comment_args = sphinx_autodoc_typehints.split_type_comment_args
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


class ObjectAlias:
	"""
	Used to represent a module, class, function etc in a Sphinx function/class signature.

	:param name: The name of the object being aliased.

	.. versionadded:: 0.9.0
	"""

	_alias_type: str

	def __init__(self, name: str):
		self.name: str = name

	def __repr__(self) -> str:
		"""
		Returns a string representation of the :class:`~.ObjectAlias`.
		"""

		return f"<{self._alias_type} {self.name!r}>"


class Module(ObjectAlias):
	"""
	Used to represent a module in a Sphinx function/class signature.

	:param name: The name of the module.
	"""

	_alias_type = "module"


class Function(ObjectAlias):
	"""
	Used to represent a function in a Sphinx function/class signature.

	:param name: The name of the function.

	.. versionadded:: 0.9.0
	"""

	_alias_type = "function"


class Class(ObjectAlias):
	"""
	Used to represent a class in a Sphinx function/class signature.

	:param name: The name of the class.

	.. versionadded:: 0.9.0
	"""

	_alias_type = "class"


def format_annotation(annotation, fully_qualified: bool = False) -> str:
	"""
	Format a type annotation.

	:param annotation:
	:param fully_qualified:
	"""

	prefix = '' if fully_qualified else '~'

	# Special cases
	if annotation is None or annotation is type(None):  # noqa: E721
		return ":py:obj:`None`"
	elif annotation is Ellipsis:
		return "..."
	elif annotation is types.GetSetDescriptorType:  # noqa E721
		return f":py:data:`{prefix}types.GetSetDescriptorType`"
	elif annotation is types.MemberDescriptorType:  # noqa E721
		return f":py:data:`{prefix}types.MemberDescriptorType`"
	elif annotation is types.MappingProxyType:  # noqa E721
		return f":py:data:`{prefix}types.MappingProxyType`"
	elif annotation is types.ModuleType:  # noqa E721
		return f":py:data:`{prefix}types.ModuleType`"
	elif annotation is ClassMethodDescriptorType:  # noqa E721
		return f":py:data:`{prefix}types.ClassMethodDescriptorType`"
	elif annotation is MethodDescriptorType:  # noqa E721
		return f":py:data:`{prefix}types.MethodDescriptorType`"
	elif annotation is MethodWrapperType:  # noqa E721
		return f":py:data:`{prefix}types.MethodWrapperType`"
	elif annotation is WrapperDescriptorType:  # noqa E721
		return f":py:data:`{prefix}types.WrapperDescriptorType`"
	elif annotation is types.BuiltinFunctionType:  # noqa E721
		return f":py:data:`{prefix}types.BuiltinFunctionType`"
	elif annotation is types.MethodType:  # noqa E721
		return f":py:data:`{prefix}types.MethodType`"
	elif isinstance(annotation, ForwardRef):
		# Unresolved forward ref
		return f":py:obj:`{prefix}.{annotation.__forward_arg__}`"
	elif annotation is type(re.compile('')):  # noqa E721
		return f":py:class:`{prefix}typing.Pattern`"

	try:
		module = get_annotation_module(annotation)
		class_name = get_annotation_class_name(annotation, module)
		args = get_annotation_args(annotation, module, class_name)
	except ValueError:
		return f":py:obj:`~.{annotation}`"

	# Redirect all typing_extensions types to the stdlib typing module
	if module == "typing_extensions":
		module = "typing"

	full_name = (module + '.' + class_name) if module != "builtins" else class_name
	prefix = '' if fully_qualified or full_name == class_name else '~'
	role = "data" if class_name in sphinx_autodoc_typehints.pydata_annotations else "class"
	args_format = "\\[{}]"
	formatted_args = ''

	# Type variables are also handled specially
	try:
		if isinstance(annotation, TypeVar) and annotation is not AnyStr:
			if sys.version_info < (3, 7):
				typevar_name = annotation.__name__
			else:
				typevar_name = (annotation.__module__ + '.' + annotation.__name__)
			return f":py:data:`{repr(annotation)} <{typevar_name}>`"
	except TypeError:
		pass

	# Some types require special handling
	if full_name == "typing.NewType":
		args_format = f"\\(:py:data:`~{annotation.__name__}`, {{}})"
		role = "func"
	elif full_name == "typing.Union" and len(args) == 2 and type(None) in args:
		full_name = "typing.Optional"
		args = tuple(x for x in args if x is not type(None))  # noqa: E721
	elif full_name == "typing.Callable" and args and args[0] is not ...:
		formatted_args = "\\[\\[" + ", ".join(format_annotation(arg) for arg in args[:-1]) + ']'
		formatted_args += ", " + format_annotation(args[-1]) + ']'
	elif full_name == "typing.Literal":
		# TODO: Bool, Enums?
		formatted_args = "\\[" + ", ".join(code_repr(arg) for arg in args) + ']'

	if args and not formatted_args:
		formatted_args = args_format.format(", ".join(format_annotation(arg, fully_qualified) for arg in args))

	return f":py:{role}:`{prefix}{full_name}`{formatted_args}"


#: Type hint for default preprocessor functions.
Preprocessor = Callable[[Type], Any]

default_preprocessors: List[Tuple[Callable[[Type], bool], Preprocessor]] = [
		(lambda d: isinstance(d, ModuleType), lambda d: Module(d.__name__)),
		(lambda d: isinstance(d, FunctionType), lambda d: Function(d.__name__)),
		(inspect.isclass, lambda d: Class(d.__name__)),
		(lambda d: d is Ellipsis, lambda d: etc),
		(lambda d: d == "...", lambda d: etc),
		]
"""
A list of 2-element tuples, comprising a function to check the default value against and a preprocessor to
pass the function to if True.
"""


def preprocess_function_defaults(obj: Callable) -> Tuple[Optional[inspect.Signature], List[inspect.Parameter]]:
	"""
	Pre-processes the default values for the arguments of a function.

	:param obj: The function.

	:return: The function signature and a list of arguments/parameters.

	.. versionadded:: 0.8.0
	"""

	try:
		signature = Signature(inspect.unwrap(obj))
	except ValueError:  # pragma: no cover
		return None, []

	parameters = []

	for param in signature.parameters.values():
		default = param.default

		if default is not inspect.Parameter.empty:
			for check, preprocessor in default_preprocessors:
				if check(default):
					default = preprocessor(default)
					break

		parameters.append(param.replace(annotation=inspect.Parameter.empty, default=default))

	return signature, parameters


def preprocess_class_defaults(
		obj: Callable
		) -> Tuple[Optional[Callable], Optional[inspect.Signature], List[inspect.Parameter]]:
	"""
	Pre-processes the default values for the arguments of a class.

	:param obj: The class.

	:return: The class signature and a list of arguments/parameters

	.. versionadded:: 0.8.0
	"""

	init = getattr(obj, "__init__", getattr(obj, "__new__", None))

	if is_namedtuple(obj):
		init = getattr(obj, "__new__")

	try:
		signature = Signature(inspect.unwrap(init))
	except ValueError:  # pragma: no cover
		return init, None, []

	parameters = []

	for argname, param in signature.parameters.items():
		default = param.default

		if default is not inspect.Parameter.empty:
			for check, preprocessor in default_preprocessors:
				if check(default):
					default = preprocessor(default)
					break

			else:
				if hasattr(obj, "__attrs_attrs__") and default is attr.NOTHING:
					# Special casing for attrs classes
					for value in obj.__attrs_attrs__:  # type: ignore
						if value.name == argname and isinstance(value.default, attr.Factory):  # type: ignore
							default = value.default.factory()

		parameters.append(param.replace(annotation=inspect.Parameter.empty, default=default))

	return init, signature, parameters


def process_signature(
		app: Sphinx,
		what: str,
		name: str,
		obj,
		options,
		signature,
		return_annotation: Any,
		) -> Optional[Tuple[str, None]]:
	"""
	Process the signature for a function/method.

	:param app: The Sphinx app
	:param what:
	:param name: The name of the object being documented.
	:param obj: The object being documented.
	:param options: Mapping of autodoc options to values.
	:param signature:
	:param return_annotation:

	:rtype:

	.. versionchanged:: 0.8.0

		Added support for factory function default values in attrs classes.
	"""

	if not callable(obj):
		return None

	original_obj = obj

	if inspect.isclass(obj):
		obj, signature, parameters = preprocess_class_defaults(obj)
	else:
		signature, parameters = preprocess_function_defaults(obj)

	obj = inspect.unwrap(obj)

	if not getattr(obj, "__annotations__", None):
		return None

	# The generated dataclass __init__() and class are weird and need extra checks
	# This helper function operates on the generated class and methods
	# of a dataclass, not an instantiated dataclass object. As such,
	# it cannot be replaced by a call to `dataclasses.is_dataclass()`.
	def _is_dataclass(name: str, what: str, qualname: str) -> bool:
		if what == 'method' and name.endswith('.__init__'):
			# generated __init__()
			return True
		if what == 'class' and qualname.endswith('.__init__'):
			# generated class
			return True
		return False

	# The generated dataclass __init__() is weird and needs the second condition
	if (
			hasattr(obj, "__qualname__") and "<locals>" in obj.__qualname__
			and not _is_dataclass(name, what, obj.__qualname__)
			):
		sphinx_autodoc_typehints.logger.warning(
				"Cannot treat a function defined as a local function: '%s'  (use @functools.wraps)", name
				)
		return None

	if parameters:
		if inspect.isclass(original_obj) or (what == "method" and name.endswith(".__init__")):
			del parameters[0]
		elif what == "method":

			try:
				outer = inspect.getmodule(obj)
				if outer is not None:
					for clsname in obj.__qualname__.split('.')[:-1]:
						outer = getattr(outer, clsname)
			except AttributeError:
				outer = None

			method_name = obj.__name__
			if method_name.startswith("__") and not method_name.endswith("__"):
				# If the method starts with double underscore (dunder)
				# Python applies mangling so we need to prepend the class name.
				# This doesn't happen if it always ends with double underscore.
				class_name = obj.__qualname__.split('.')[-2]
				method_name = f"_{class_name}{method_name}"

			if outer is not None:
				method_object = outer.__dict__[method_name] if outer else obj
				if not isinstance(method_object, (classmethod, staticmethod)):
					del parameters[0]

			else:
				if not inspect.ismethod(obj) and parameters[0].name in {"self", "cls", "_cls"}:
					del parameters[0]

	signature = signature.replace(parameters=parameters, return_annotation=inspect.Signature.empty)

	return stringify_signature(signature), None  # .replace('\\', '\\\\')


def _docstring_property_hook(obj: Any) -> Callable:
	if isinstance(obj, property):
		obj = obj.fget

	return obj


def _docstring_class_hook(obj: Any) -> Callable:
	if callable(obj):
		if inspect.isclass(obj):
			obj = getattr(obj, "__init__")

	return obj


def _docstring_namedtuple_hook(obj: Any) -> Callable:
	if is_namedtuple(obj):
		obj = getattr(obj, "__new__")

	return obj


docstring_hooks: List[Tuple[Callable[[Any], Callable], int]] = [
		(_docstring_property_hook, 20),
		(_docstring_namedtuple_hook, 90),
		(_docstring_class_hook, 100),
		]
"""
List of additional hooks to run in :func:`~sphinx_toolbox.more_autodoc.typehints.process_docstring`.

Each entry in the list consists of:

* a function that takes the object being documented as its only argument
  and returns that object after modification.

* a number giving the priority of the hook, in ascending order.

   * ``< 20`` runs before ``fget`` functions are extracted from properties
   * ``< 90`` runs before ``__new__`` functions are extracted from :class:`NamedTuples <typing.NamedTuple>`.
   * ``< 100`` runs before ``__init__`` functions are extracted from classes.
"""


def process_docstring(
		app: Sphinx,
		what: str,
		name: str,
		obj: Any,
		options: Dict[str, Any],
		lines: List[str],
		) -> None:
	"""
	Process the docstring of a class, function, method etc.

	:param app: The Sphinx app
	:param what:
	:param name: The name of the object being documented
	:param obj: The object being documented.
	:param options: Mapping of autodoc options to values.
	:param lines: List of strings representing the current contents of the docstring.

	.. versionchanged:: 1.1.0

		An empty ``:rtype:`` flag can be used to control the position of the return type annotation in the docstring.
	"""

	original_obj = obj

	for hook, priority in sorted(docstring_hooks, key=operator.itemgetter(1)):
		obj = hook(obj)

	if callable(obj):
		obj = inspect.unwrap(obj)
		type_hints = get_all_type_hints(obj, name, original_obj)

		for argname, annotation in type_hints.items():
			if argname == "return":
				continue  # this is handled separately later

			argname = escape_trailing__(argname)

			formatted_annotation = format_annotation(
					annotation,
					fully_qualified=app.config.typehints_fully_qualified,  # type: ignore
					)

			searchfor = [f":{field} {argname}:" for field in ("param", "parameter", "arg", "argument")]
			insert_index = None

			for i, line in enumerate(lines):
				if any(line.startswith(search_string) for search_string in searchfor):
					insert_index = i
					break

			if insert_index is None and app.config.always_document_param_types:  # type: ignore
				lines.append(f":param {argname}:")
				insert_index = len(lines)

			if insert_index is not None:
				lines.insert(insert_index, f":type {argname}: {formatted_annotation}")

		if "return" in type_hints and not inspect.isclass(original_obj):
			# This avoids adding a return type for data class __init__ methods
			if what == "method" and name.endswith(".__init__"):
				return

			formatted_annotation = format_annotation(
					type_hints["return"],
					fully_qualified=app.config.typehints_fully_qualified,  # type: ignore
					)

			insert_index = len(lines)
			for i, line in enumerate(lines):
				if line.startswith(":rtype:"):
					if line[7:].strip():
						insert_index = None
					else:
						insert_index = i
						lines.pop(i)

					break

				elif line.startswith(":return:") or line.startswith(":returns:"):
					insert_index = i

			if insert_index is not None and app.config.typehints_document_rtype:  # type: ignore

				if insert_index == len(lines):
					# Ensure that :rtype: doesn't get joined with a paragraph of text, which
					# prevents it being interpreted.
					lines.append('')
					insert_index += 1

				if not (formatted_annotation == ":py:obj:`None`" and app.config.hide_none_rtype):  # type: ignore
					lines.insert(insert_index, f":rtype: {formatted_annotation}")


def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.typehints`.

	:param app: The Sphinx app
	"""

	if "sphinx_autodoc_typehints" in app.extensions:
		raise ExtensionError(
				"'sphinx_toolbox.more_autodoc.typehints' must be loaded before 'sphinx_autodoc_typehints."
				)

	sphinx_autodoc_typehints.format_annotation = format_annotation
	sphinx_autodoc_typehints.process_signature = process_signature
	sphinx_autodoc_typehints.process_docstring = process_docstring

	app.setup_extension("sphinx.ext.autodoc")
	app.setup_extension("sphinx_autodoc_typehints")

	app.add_config_value("hide_none_rtype", False, "env", [bool])

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}


def _class_get_type_hints(obj, globalns=None, localns=None):
	"""
	Return type hints for an object.

	For classes, unlike :func:`typing.get_type_hints` this will attempt to
	use the global namespace of the modules where the class and its parents
	were defined until it can resolve all forward references.
	"""

	if not inspect.isclass(obj):
		return get_type_hints(obj, localns=localns, globalns=globalns)

	mro_stack = list(obj.__mro__)
	if localns is None:
		localns = {}

	while True:

		try:
			return get_type_hints(obj.__init__, localns=localns, globalns=globalns)
		except NameError:
			if not mro_stack:
				raise
			klasse = mro_stack.pop(0)
			if klasse is object or klasse.__module__ == "builtins":
				raise
			localns = {**sys.modules[klasse.__module__].__dict__, **localns}


def get_all_type_hints(obj, name, original_obj):
	"""
	Returns the resolved type hints for the given objects.

	:param obj:
	:param name:
	:param original_obj: The original object, before the class if ``obj`` is its ``__init__`` method.
	"""

	def log(exc):
		sphinx_autodoc_typehints.logger.warning(
				'Cannot resolve forward reference in type annotations of "%s": %s',
				name,
				exc,
				)

	rv = {}

	try:
		if inspect.isclass(original_obj):
			rv = _class_get_type_hints(original_obj)
		else:
			rv = get_type_hints(obj)
	except (AttributeError, TypeError, RecursionError):
		# Introspecting a slot wrapper will raise TypeError, and some recursive type
		# definitions will cause a RecursionError (https://github.com/python/typing/issues/574).
		pass
	except NameError as exc:
		log(exc)
		rv = obj.__annotations__

	if rv:
		return rv

	rv = backfill_type_hints(obj, name)

	try:
		if rv != {}:
			obj.__annotations__ = rv
	except (AttributeError, TypeError):
		return rv

	try:
		if inspect.isclass(original_obj):
			rv = _class_get_type_hints(original_obj)
		else:
			rv = get_type_hints(obj)
	except (AttributeError, TypeError):
		pass
	except NameError as exc:
		log(exc)
		rv = obj.__annotations__

	return rv

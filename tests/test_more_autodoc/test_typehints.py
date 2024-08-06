# stdlib
import ast
import io
import itertools
import re
import sys
import types
import typing
from email.headerregistry import Address
from tempfile import TemporaryDirectory
from typing import Any, List

# 3rd party
import pytest
from coincidence.selectors import max_version, min_version, not_pypy, only_pypy
from domdf_python_tools.typing import (
		ClassMethodDescriptorType,
		MethodDescriptorType,
		MethodWrapperType,
		WrapperDescriptorType
		)
from sphinx.errors import ExtensionError
from typing_extensions import Literal, Protocol

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import typehints
from sphinx_toolbox.testing import Sphinx, run_setup
from tests.common import get_app_config_values

if sys.version_info >= (3, 10):
	UnionType = types.UnionType
else:
	UnionType = None


@pytest.mark.parametrize(
		"annotation, expected",
		[
				pytest.param(True, ":py:obj:`True`", id="True"),
				pytest.param(False, ":py:obj:`False`", id="False"),
				pytest.param(None, ":py:obj:`None`", id="None"),
				pytest.param(type(None), ":py:obj:`None`", id="NoneType"),
				pytest.param(Ellipsis, "...", id="Ellipsis"),
				pytest.param(..., "...", id="..."),
				pytest.param(itertools.cycle, ":func:`itertools.cycle`", id="itertools.cycle"),
				pytest.param(
						types.GetSetDescriptorType,
						":py:data:`types.GetSetDescriptorType`",
						id="types.GetSetDescriptorType"
						),
				pytest.param(
						types.MemberDescriptorType,
						":py:data:`types.MemberDescriptorType`",
						id="types.MemberDescriptorType"
						),
				pytest.param(
						ClassMethodDescriptorType,
						":py:data:`types.ClassMethodDescriptorType`",
						id="types.ClassMethodDescriptorType"
						),
				pytest.param(
						typing.ContextManager[str],
						r":py:class:`contextlib.AbstractContextManager`\[:py:class:`str`]",
						id="typing.ContextManager",
						marks=max_version("3.9"),
						),
				pytest.param(
						MethodDescriptorType,
						":py:data:`types.MethodDescriptorType`",
						id="types.MethodDescriptorType",
						marks=not_pypy("PyPy reuses some types"),
						),
				pytest.param(
						MethodDescriptorType,
						":py:data:`types.FunctionType`",
						id="types.MethodDescriptorType",
						marks=only_pypy("PyPy reuses some types"),
						),
				pytest.param(
						MethodWrapperType,
						":py:data:`types.MethodWrapperType`",
						id="types.MethodWrapperType",
						marks=not_pypy("PyPy reuses some types"),
						),
				pytest.param(
						MethodWrapperType,
						":py:data:`types.MethodType`",
						id="types.MethodWrapperType",
						marks=only_pypy("PyPy reuses some types"),
						),
				pytest.param(
						WrapperDescriptorType,
						":py:data:`types.WrapperDescriptorType`",
						id="types.WrapperDescriptorType",
						marks=not_pypy("PyPy reuses some types")
						),
				pytest.param(
						WrapperDescriptorType,
						":py:data:`types.FunctionType`",
						id="types.WrapperDescriptorType",
						marks=only_pypy("PyPy reuses some types")
						),
				pytest.param(
						types.BuiltinFunctionType,
						":py:data:`types.BuiltinFunctionType`",
						id="types.BuiltinFunctionType"
						),
				pytest.param(types.FunctionType, ":py:data:`types.FunctionType`", id="types.FunctionType"),
				pytest.param(
						types.MethodType,
						":py:data:`types.MethodType`",
						id="types.MethodType",
						),
				pytest.param(
						types.MappingProxyType, ":py:class:`types.MappingProxyType`", id="types.MappingProxyType"
						),
				pytest.param(types.ModuleType, ":py:class:`types.ModuleType`", id="types.ModuleType"),
				pytest.param(type(re.compile('')), ":py:class:`typing.Pattern`", id="regex"),
				pytest.param(List, ":py:class:`typing.List`", id="typing.List"),
				pytest.param(Protocol, ":py:class:`typing.Protocol`", id="typing_extensions.Protocol"),
				pytest.param(
						Address, ":py:class:`email.headerregistry.Address`", id="email.headerregistry.Address"
						),
				pytest.param(io.StringIO, ":py:class:`io.StringIO`", id="io.StringIO"),
				pytest.param(ast.AST, ":py:class:`ast.AST`", id="ast.AST"),
				pytest.param(
						TemporaryDirectory,
						":py:obj:`tempfile.TemporaryDirectory`",
						id="tempfile.TemporaryDirectory"
						),
				pytest.param(Literal[True], r":py:data:`typing.Literal`\[:py:obj:`True`]", id="Literal_True"),
				pytest.param(Literal[False], r":py:data:`typing.Literal`\[:py:obj:`False`]", id="Literal_False"),
				pytest.param(
						Literal[True, "Hello"],
						r":py:data:`typing.Literal`\[:py:obj:`True`, ``'Hello'``]",
						id="Literal_True_String"
						),
				pytest.param(
						Literal[True, 123],
						r":py:data:`typing.Literal`\[:py:obj:`True`, ``123``]",
						id="Literal_True_Int"
						),
				pytest.param(
						UnionType,
						":py:data:`types.UnionType`",
						id="types.UnionType",
						marks=min_version("3.10", reason="Introduced in 3.10")
						),
				]
		)
def test_format_annotation(annotation: Any, expected: str):
	assert typehints.format_annotation(annotation, True) == expected


def test_setup():
	try:
		Sphinx.extensions = []  # type: ignore[attr-defined]

		setup_ret, directives, roles, additional_nodes, app = run_setup(typehints.setup)

		assert setup_ret == {"parallel_read_safe": True, "version": __version__}

		assert get_app_config_values(app.config.values["hide_none_rtype"]) == (False, "env", [bool])

		assert directives == {}
		assert roles == {}
		assert additional_nodes == set()

	finally:
		del Sphinx.extensions  # type: ignore[attr-defined]


def test_setup_wrong_order():
	try:
		Sphinx.extensions = ["sphinx_autodoc_typehints"]  # type: ignore[attr-defined]

		with pytest.raises(
				ExtensionError,
				match="'sphinx_toolbox.more_autodoc.typehints' "
				"must be loaded before 'sphinx_autodoc_typehints'.",
				):

			run_setup(typehints.setup)

	finally:
		del Sphinx.extensions  # type: ignore[attr-defined]

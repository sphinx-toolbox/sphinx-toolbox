# stdlib
import ast
import io
import itertools
import re
import types
from email.headerregistry import Address
from typing import Any, List

# 3rd party
import pytest
from domdf_python_tools.typing import (
		ClassMethodDescriptorType,
		MethodDescriptorType,
		MethodWrapperType,
		WrapperDescriptorType
		)
from typing_extensions import Protocol

# this package
from sphinx_toolbox.more_autodoc.typehints import format_annotation


@pytest.mark.parametrize(
		"annotation, expected",
		[
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
						MethodDescriptorType,
						":py:data:`types.MethodDescriptorType`",
						id="types.MethodDescriptorType"
						),
				pytest.param(
						MethodWrapperType, ":py:data:`types.MethodWrapperType`", id="types.MethodWrapperType"
						),
				pytest.param(
						WrapperDescriptorType,
						":py:data:`types.WrapperDescriptorType`",
						id="types.WrapperDescriptorType"
						),
				pytest.param(
						types.BuiltinFunctionType,
						":py:data:`types.BuiltinFunctionType`",
						id="types.BuiltinFunctionType"
						),
				pytest.param(types.MethodType, ":py:data:`types.MethodType`", id="types.MethodType"),
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
				]
		)
def test_format_annotation(annotation: Any, expected: str):
	assert format_annotation(annotation, True) == expected

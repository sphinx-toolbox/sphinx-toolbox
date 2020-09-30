# stdlib
from typing import Any, Dict, List, NamedTuple, Sequence, Type, Union, no_type_check

# 3rd party
from domdf_python_tools.secrets import Secret

# this package
from sphinx_toolbox.more_autodoc.variables import get_variable_type


class Foo:
	a: str
	b: int
	c: float
	d: "float"
	e: "List"


class Bar:
	a: str
	b: int
	c: float
	d: "float"
	e: "List"
	f: "Set"  # type: ignore

	def __init__(self):
		self.g: Secret = Secret("")
		self.h: "Secret" = Secret("")


class Analyzer(NamedTuple):
	annotations: Dict[Sequence[str], Any]


class Documenter(NamedTuple):
	parent: Type
	objpath: List[str]
	analyzer: Analyzer


@no_type_check
def test_get_variable_type():
	assert get_variable_type(Documenter(Foo, ["Foo", "a"], Analyzer({}))) == ":py:class:`str`"
	assert get_variable_type(Documenter(Foo, ["Foo", "b"], Analyzer({}))) == ":py:class:`int`"
	assert get_variable_type(Documenter(Foo, ["Foo", "c"], Analyzer({}))) == ":py:class:`float`"
	assert get_variable_type(Documenter(Foo, ["Foo", "d"], Analyzer({}))) == ":py:class:`float`"
	assert get_variable_type(Documenter(Foo, ["Foo", "e"], Analyzer({}))) == ":py:class:`~typing.List`"

	assert get_variable_type(Documenter(Bar, ["Bar", "a"], Analyzer({}))) == ":py:class:`str`"
	assert get_variable_type(Documenter(Bar, ["Bar", "b"], Analyzer({}))) == ":py:class:`int`"
	assert get_variable_type(Documenter(Bar, ["Bar", "c"], Analyzer({}))) == ":py:class:`float`"
	# Failed forward reference throws everything else out of whack
	assert get_variable_type(Documenter(Bar, ["Bar", "d"], Analyzer({}))) == ":py:obj:`~.float`"
	assert get_variable_type(Documenter(Bar, ["Bar", "e"], Analyzer({}))) == ":py:obj:`~.List`"
	assert get_variable_type(Documenter(Bar, ["Bar", "f"], Analyzer({}))) == ":py:obj:`~.Set`"
	assert get_variable_type(Documenter(Bar, ["Bar", "g"], Analyzer({}))) == ''
	# assert get_variable_type(Documenter(Bar, ["Bar", "g"], Analyzer({("Bar", "g"): "Secret"}))) == ":py:class:`~domdf_python_tools.secrets.Secret`"
	assert get_variable_type(
			Documenter(Bar, ["Bar", "h"], Analyzer({("Bar", "h"): "'Secret'"}))
			) == ":py:class:`~domdf_python_tools.secrets.Secret`"
	assert get_variable_type(
			Documenter(Bar, ["Bar", "h"], Analyzer({("Bar", "h"): '"Secret"'}))
			) == ":py:class:`~domdf_python_tools.secrets.Secret`"
	assert get_variable_type(
			Documenter(Bar, ["Bar", "h"], Analyzer({("Bar", "h"): "Union[str, float, int]"}))
			) == ":py:data:`~typing.Union`\\[:py:class:`str`, :py:class:`float`, :py:class:`int`]"
	assert get_variable_type(
			Documenter(Bar, ["Bar", "h"], Analyzer({("Bar", "h"): "'Union[str, float, int]'"}))
			) == ":py:data:`~typing.Union`\\[:py:class:`str`, :py:class:`float`, :py:class:`int`]"
	assert get_variable_type(
			Documenter(Bar, ["Bar", "h"], Analyzer({("Bar", "h"): '"Union[str, float, int]"'}))
			) == ":py:data:`~typing.Union`\\[:py:class:`str`, :py:class:`float`, :py:class:`int`]"

	assert get_variable_type(Documenter('Bar', ["Bar", "f"], Analyzer({}))) == ''

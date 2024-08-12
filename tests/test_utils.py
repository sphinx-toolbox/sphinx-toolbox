# stdlib
import collections
import inspect
import string
import sys
from typing import List, NamedTuple

# 3rd party
import pytest
from apeye.requests_url import RequestsURL
from domdf_python_tools.utils import strtobool
from hypothesis import given
from hypothesis.strategies import text
from sphinx.application import Sphinx

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.utils import (
		NoMatchError,
		Purger,
		SphinxExtMetadata,
		code_repr,
		escape_trailing__,
		flag,
		get_first_matching,
		is_namedtuple,
		make_github_url,
		metadata_add_version,
		parse_parameters,
		singleton
		)


def test_make_github_url():
	url = make_github_url("domdfcoding", "sphinx-toolbox")
	assert isinstance(url, RequestsURL)

	assert url == RequestsURL("https://github.com/domdfcoding/sphinx-toolbox")


def test_flag():
	assert flag('')
	assert flag(' ')
	assert flag("  ")
	assert flag("   ")
	assert flag("    ")
	assert flag('\t')

	assert flag(False)

	with pytest.raises(AttributeError):
		flag(True)

	with pytest.raises(ValueError, match="No argument is allowed; 'hello' supplied"):
		flag("hello")


class MockBuildEnvironment:
	pass


demo_purger = Purger("all_demo_nodes")


@pytest.mark.parametrize(
		"nodes, output",
		[
				([], []),
				([{"docname": "document"}], []),
				([{"docname": "foo"}], [{"docname": "foo"}]),
				([{"docname": "foo"}, {"docname": "document"}], [{"docname": "foo"}]),
				]
		)
def test_purge_extras_require(nodes: List[str], output: List[str]):
	env = MockBuildEnvironment()

	demo_purger.purge_nodes('', env, "document")  # type: ignore[arg-type]
	assert not hasattr(env, "all_extras_requires")

	env.all_demo_nodes = nodes  # type: ignore[attr-defined]
	demo_purger.purge_nodes('', env, "document")  # type: ignore[arg-type]
	assert hasattr(env, "all_demo_nodes")
	assert env.all_demo_nodes == output


def test_get_first_matching():

	assert get_first_matching(strtobool, [True, "True", 0, "False", False])
	assert get_first_matching(strtobool, (True, "True", 0, "False", False))

	with pytest.raises(
			NoMatchError,
			match=r"No matching values for '<function strtobool at .*>' in \[0, 'False', False\]",
			):
		get_first_matching(strtobool, [0, "False", False])

	assert get_first_matching(strtobool, [0, "False", False], default=True)

	assert get_first_matching(lambda x: x.isupper(), string.ascii_letters) == 'A'

	with pytest.raises(
			ValueError,
			match="The condition must evaluate to True for the default value.",
			):
		get_first_matching(lambda x: x.isdigit(), string.ascii_letters, default='A')


def test_singleton():

	s = singleton('s')

	assert str(s) == 's'
	assert repr(s) == 's'

	assert s is s
	assert s is s.__class__()
	assert s is type(s)()


@given(text(alphabet=string.ascii_letters + string.digits, min_size=1))
def test_escape_trailing_underscore(s: str):

	assert escape_trailing__(s) == s

	assert escape_trailing__(f"{s}_") == rf"{s}\_"
	assert escape_trailing__(f"{s}__") == rf"{s}_\_"
	assert escape_trailing__(f"_{s}") == f"_{s}"


@pytest.mark.parametrize(
		"value, expected", [
				pytest.param("hello", "``'hello'``"),
				pytest.param("it's me!", "``\"it's me!\"``"),
				]
		)
def test_code_repr(value: str, expected: str):
	assert code_repr(value) == expected


@pytest.mark.xfail(
		sys.version_info >= (3, 13),
		reason="Tabs are now converted into 8 spaces unconditionally (see python/cpython#81283)"
		)
def test_parse_parameters():
	docstring = inspect.cleandoc((parse_parameters.__doc__ or '').expandtabs(4))

	docstring_dict = {
			"lines": {"doc": ["The lines of the docstring"], "type": ''},
			"tab_size": {"doc": [''], "type": ''},
			}
	pre_output = [
			"Parse parameters from the docstring of a class/function.",
			'',
			".. versionadded:: 0.8.0",
			'',
			]
	post_output = [
			'',
			":return: A mapping of parameter names to their docstrings and types, a list of docstring lines that",
			"    appeared before the parameters, and the list of docstring lines that appear after the parameters.",
			]

	assert parse_parameters(docstring.split('\n'), tab_size=4) == (docstring_dict, pre_output, post_output)


class NT(NamedTuple):
	foo: str
	bar: int


@pytest.mark.parametrize(
		"obj, result",
		[
				pytest.param("abc", False, id="str"),
				pytest.param(123, False, id="int"),
				pytest.param(123.456, False, id="float"),
				pytest.param(("abc", 123), False, id="tuple"),
				pytest.param(
						collections.namedtuple("Foo", "str, int")("abc", 123),  # type: ignore[call-arg]
						False,
						id="namedtuple",
						),
				pytest.param(NT("abc", 123), False, id="typing.NamedTuple"),
				pytest.param(str, False, id="type str"),
				pytest.param(int, False, id="type int"),
				pytest.param(float, False, id="type float"),
				pytest.param(tuple, False, id="type tuple"),
				pytest.param(collections.namedtuple("Foo", "str, int"), True, id="type namedtuple"),
				pytest.param(NT, True, id="type typing.NamedTuple"),
				]
		)
def test_is_namedtuple(obj: object, result: bool):
	assert is_namedtuple(obj) is result


def test_metadata_add_version():

	@metadata_add_version
	def setup(app: Sphinx) -> SphinxExtMetadata:
		return {"parallel_read_safe": True}

	assert setup(None) == {"parallel_read_safe": True, "version": __version__}  # type: ignore[arg-type]

# stdlib
from typing import Any, Dict, List, NamedTuple, Sequence, Type, Union, no_type_check  # noqa: F401

# 3rd party
import pytest
from coincidence import PEP_563
from domdf_python_tools.secrets import Secret
from sphinx.ext.autodoc.directive import AutodocDirective

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import variables
from sphinx_toolbox.more_autodoc.variables import get_variable_type
from sphinx_toolbox.testing import run_setup


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
	f: "Set"  # type: ignore[name-defined]

	def __init__(self):
		self.g: Secret = Secret('')
		self.h: "Secret" = Secret('')


class Analyzer(NamedTuple):
	annotations: Dict[Sequence[str], Any]


class Documenter(NamedTuple):
	parent: Type
	objpath: List[str]
	analyzer: Analyzer


variable_params = [
		((Documenter(Foo, ["Foo", 'a'], Analyzer({}))), ":py:class:`str`"),
		((Documenter(Foo, ["Foo", 'b'], Analyzer({}))), ":py:class:`int`"),
		((Documenter(Foo, ["Foo", 'c'], Analyzer({}))), ":py:class:`float`"),
		((Documenter(Foo, ["Foo", 'd'], Analyzer({}))), ":py:class:`float`"),
		((Documenter(Foo, ["Foo", 'e'], Analyzer({}))), ":py:class:`~typing.List`"),

		# On 3.10 with PEP 563 failed forward references break things earlier
		pytest.param(
				(Documenter(Bar, ["Bar", 'a'], Analyzer({}))),
				":py:obj:`~.str`",
				marks=pytest.mark.skipif(not PEP_563, reason="Output differs post PEP 563"),
				),
		pytest.param(
				(Documenter(Bar, ["Bar", 'b'], Analyzer({}))),
				":py:obj:`~.int`",
				marks=pytest.mark.skipif(not PEP_563, reason="Output differs post PEP 563"),
				),
		pytest.param(
				(Documenter(Bar, ["Bar", 'c'], Analyzer({}))),
				":py:obj:`~.float`",
				marks=pytest.mark.skipif(not PEP_563, reason="Output differs post PEP 563"),
				),
		pytest.param(
				(Documenter(Bar, ["Bar", 'a'], Analyzer({}))),
				":py:class:`str`",
				marks=pytest.mark.skipif(PEP_563, reason="Output differs pre PEP 563"),
				),
		pytest.param(
				(Documenter(Bar, ["Bar", 'b'], Analyzer({}))),
				":py:class:`int`",
				marks=pytest.mark.skipif(PEP_563, reason="Output differs pre PEP 563"),
				),
		pytest.param(
				(Documenter(Bar, ["Bar", 'c'], Analyzer({}))),
				":py:class:`float`",
				marks=pytest.mark.skipif(PEP_563, reason="Output differs pre PEP 563"),
				),

		# Failed forward reference throws everything else out of whack
		((Documenter(Bar, ["Bar", 'd'], Analyzer({}))), ":py:obj:`~.float`"),
		((Documenter(Bar, ["Bar", 'e'], Analyzer({}))), ":py:obj:`~.List`"),
		((Documenter(Bar, ["Bar", 'f'], Analyzer({}))), ":py:obj:`~.Set`"),
		((Documenter(Bar, ["Bar", 'g'], Analyzer({}))), ''),
		# ((Documenter(Bar, ["Bar", "g"], Analyzer({("Bar", "g"): "Secret"}))), ":py:class:`~domdf_python_tools.secrets.Secret`"),
		(
				(Documenter(Bar, ["Bar", 'h'], Analyzer({("Bar", 'h'): "'Secret'"}))),
				":py:class:`~domdf_python_tools.secrets.Secret`",
				),
		(
				(Documenter(Bar, ["Bar", 'h'], Analyzer({("Bar", 'h'): '"Secret"'}))),
				":py:class:`~domdf_python_tools.secrets.Secret`",
				),
		(
				(Documenter(Bar, ["Bar", 'h'], Analyzer({("Bar", 'h'): "Union[str, float, int]"}))),
				":py:class:`~typing.Union`\\[:py:class:`str`, :py:class:`float`, :py:class:`int`]",
				),
		(
				(Documenter(Bar, ["Bar", 'h'], Analyzer({("Bar", 'h'): "'Union[str, float, int]'"}))),
				":py:class:`~typing.Union`\\[:py:class:`str`, :py:class:`float`, :py:class:`int`]",
				),
		(
				(Documenter(Bar, ["Bar", 'h'], Analyzer({("Bar", 'h'): '"Union[str, float, int]"'}))),
				":py:class:`~typing.Union`\\[:py:class:`str`, :py:class:`float`, :py:class:`int`]",
				),
		(
				(Documenter("Bar", ["Bar", 'f'], Analyzer({}))),  # type: ignore[arg-type]
				'',
				),
		]


@pytest.mark.parametrize("documenter, expected", variable_params)
def test_get_variable_type(documenter: Documenter, expected: str):
	assert get_variable_type(documenter) == expected  # type: ignore[arg-type]


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(variables.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {
			"autovariable": AutodocDirective,
			"autoattribute": AutodocDirective,
			"autoinstanceattribute": AutodocDirective,
			"autoslotsattribute": AutodocDirective,
			"autoproperty": AutodocDirective,
			}

	assert roles == {}
	assert additional_nodes == set()

	assert app.registry.documenters["variable"] == variables.VariableDocumenter
	assert app.registry.documenters["attribute"] == variables.TypedAttributeDocumenter
	assert app.registry.documenters["instanceattribute"] == variables.InstanceAttributeDocumenter
	assert app.registry.documenters["slotsattribute"] == variables.SlotsAttributeDocumenter
	assert app.registry.documenters["property"] == variables.PropertyDocumenter

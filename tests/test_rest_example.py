# 3rd party
from sphinx.events import EventListener

# this package
from sphinx_toolbox import rest_example
from sphinx_toolbox.rest_example import make_rest_example, rest_example_purger, reSTExampleDirective
from sphinx_toolbox.testing import run_setup
from tests.common import AttrDict


class FakeBuildEnvironment(AttrDict):

	def __init__(self, tab_width: int):
		config = AttrDict({"docutils_tab_width": tab_width})
		super().__init__({"config": config})


def test_make_rest_example():

	assert make_rest_example(
			{},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			[],
			) == [".. container:: rest-example", '', "    .. code-block:: rest", '']

	assert make_rest_example(
			{"hello": "world"},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			[],
			) == [".. container:: rest-example", '', "    .. code-block:: rest", "        :hello: world", '']

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			[],
			) == [
					".. container:: rest-example",
					'',
					"    .. code-block:: rest",
					"        :hello: world",
					"        :flag:",
					''
					]

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			["this is some content"],
			) == [
					".. container:: rest-example",
					'',
					"    .. code-block:: rest",
					"        :hello: world",
					"        :flag:",
					'',
					"        this is some content",
					'',
					"    this is some content",
					'',
					]

	assert make_rest_example(
			{},
			FakeBuildEnvironment(8),  # type: ignore[arg-type]
			[],
			) == [".. container:: rest-example", '', "        .. code-block:: rest", '']

	assert make_rest_example(
			{"hello": "world"},
			FakeBuildEnvironment(8),  # type: ignore[arg-type]
			[],
			) == [
					".. container:: rest-example",
					'',
					"        .. code-block:: rest",
					"                :hello: world",
					'',
					]

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(8),  # type: ignore[arg-type]
			[],
			) == [
					".. container:: rest-example",
					'',
					"        .. code-block:: rest",
					"                :hello: world",
					"                :flag:",
					'',
					]

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(8),  # type: ignore[arg-type]
			["this is some content"],
			) == [
					".. container:: rest-example",
					'',
					"        .. code-block:: rest",
					"                :hello: world",
					"                :flag:",
					'',
					"                this is some content",
					'',
					"        this is some content",
					'',
					]


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(rest_example.setup)

	assert app.events.listeners == {
			"env-purge-doc": [EventListener(id=0, handler=rest_example_purger.purge_nodes, priority=500)],
			}

	assert directives == {
			"rest-example": reSTExampleDirective,
			}

	assert app.registry.source_parsers == {}

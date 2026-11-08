# 3rd party
import pytest
from docutils import nodes
from domdf_python_tools.paths import PathPlus
from sphinx import addnodes
from sphinx.application import Sphinx
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
			) == ['', ".. code-block:: rest", '']

	assert make_rest_example(
			{"hello": "world"},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			[],
			) == ['', ".. code-block:: rest", "    :hello: world", '']

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			[],
			) == [
					'',
					".. code-block:: rest",
					"    :hello: world",
					"    :flag:",
					'',
					]

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(4),  # type: ignore[arg-type]
			["this is some content"],
			) == [
					'',
					".. code-block:: rest",
					"    :hello: world",
					"    :flag:",
					'',
					"    this is some content",
					'',
					"this is some content",
					'',
					]

	assert make_rest_example(
			{},
			FakeBuildEnvironment(8),  # type: ignore[arg-type]
			[],
			) == ['', ".. code-block:: rest", '']

	assert make_rest_example(
			{"hello": "world"},
			FakeBuildEnvironment(8),  # type: ignore[arg-type]
			[],
			) == [
					'',
					".. code-block:: rest",
					"        :hello: world",
					'',
					]

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(8),  # type: ignore[arg-type]
			[],
			) == [
					'',
					".. code-block:: rest",
					"        :hello: world",
					"        :flag:",
					'',
					]

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(8),  # type: ignore[arg-type]
			["this is some content"],
			) == [
					'',
					".. code-block:: rest",
					"        :hello: world",
					"        :flag:",
					'',
					"        this is some content",
					'',
					"this is some content",
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


@pytest.fixture()
def glossary_doc_root(tmp_pathplus: PathPlus) -> None:
	doc_root = tmp_pathplus.parent / "test-rest-example-glossary"
	doc_root.maybe_make()
	(doc_root / "conf.py").write_clean("extensions = ['sphinx_toolbox.rest_example']")
	(doc_root / "index.rst").write_lines([
			"Title",
			"=====",
			'',
			".. rest-example::",
			'',
			"\t.. glossary::",
			'',
			"\t\tterm",
			"\t\t\tDefinition of the term.",
			])


@pytest.mark.usefixtures("glossary_doc_root")
@pytest.mark.sphinx("html", testroot="test-rest-example-glossary")
def test_rest_example_glossary(app: Sphinx):
	# A ``glossary`` inside ``rest-example`` used to crash with
	# "TypeError: extending a ViewList with a non-ViewList".
	# https://github.com/sphinx-toolbox/sphinx-toolbox/issues/207

	app.build()

	doctree = app.env.get_doctree("index")
	glossaries = list(getattr(doctree, "findall", doctree.traverse)(addnodes.glossary))
	assert len(glossaries) == 1
	terms = list(getattr(glossaries[0], "findall", glossaries[0].traverse)(nodes.term))
	assert [term.astext() for term in terms] == ["term"]

# 3rd party
import sphinx
from apeye.requests_url import RequestsURL
from docutils.nodes import inline, reference, system_message
from docutils.utils import Reporter
from sphinx import addnodes
from sphinx.events import EventListener

# this package
from sphinx_toolbox import source
from sphinx_toolbox.source import source_role
from sphinx_toolbox.testing import run_setup
from tests.common import AttrDict


class FakeSourceInliner:

	def __init__(self, source_link_target, github_source_url):
		config = AttrDict({
				"source_link_target": source_link_target,
				"github_source_url": RequestsURL(github_source_url),
				})
		app = AttrDict({"config": config, "builder": AttrDict({"get_relative_uri": lambda from_, to: to})})
		env = AttrDict({"app": app, "docname": ''})
		settings = AttrDict({"env": env})
		reporter = Reporter('', 0, 100)

		self.document = AttrDict({"settings": settings, "reporter": reporter})


def test_source_role_github():
	github_source_url = "https://github.com/python/cpython/blob/master"
	nodes, messages = source_role('', '', "Lib/typing.py", 0, FakeSourceInliner("github", github_source_url))  # type: ignore[arg-type]

	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], reference)
	ref_node: reference = nodes[0]
	assert ref_node.attributes["refuri"] == "https://github.com/python/cpython/blob/master/Lib/typing.py"
	assert ref_node.rawsource == "Lib/typing.py"


def test_source_role_sphinx():
	nodes, messages = source_role('', '', "Lib/typing.py", 0, FakeSourceInliner("sphinx", ''))  # type: ignore[arg-type]

	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages

	if sphinx.version_info[:3] < (3, 5, 0):
		assert isinstance(nodes[0], addnodes.pending_xref)
		assert isinstance(nodes[0].children[0], inline)
		assert nodes[0].attributes["reftype"] == "viewcode"
		assert nodes[0].attributes["refdomain"] == "std"
		assert nodes[0].attributes["reftarget"] == "_modules/Lib/typing"
		assert nodes[0].attributes["refid"] == "Lib/typing.py"
		assert not nodes[0].attributes["refexplicit"]

	else:
		assert isinstance(nodes[0], reference)
		assert isinstance(nodes[0].children[0], inline)
		assert nodes[0].attributes["refuri"] == "_modules/Lib/typing#Lib/typing.py"
		assert "reftitle" not in nodes[0].attributes
		assert "refid" not in nodes[0].attributes
		assert nodes[0].attributes["internal"] is True


def test_source_role_unknown_target(capsys):
	nodes, messages = source_role('', '', "Lib/typing.py", 0, FakeSourceInliner("gitlab", ''))  # type: ignore[arg-type]
	assert capsys.readouterr().err == ":: (ERROR/3) Unsupported source link target 'gitlab'.\n"

	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not nodes
	assert isinstance(messages[0], system_message)
	assert messages[0].astext() == ":: (ERROR/3) Unsupported source link target 'gitlab'."


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(source.setup)

	assert roles == {"source": source.source_role}
	assert app.config.values["source_link_target"] == ("Sphinx", "env", [str])
	assert app.registry.source_parsers == {}
	assert app.events.listeners == {"config-inited": [EventListener(0, source._configure, 500)]}

# stdlib
from typing import Any, Dict

# 3rd party
import pytest
from docutils.nodes import NodeVisitor
from docutils.transforms import Transform
from pygments.lexer import Lexer
from sphinx.builders import Builder
from sphinx.domains import Domain
from sphinx.events import EventListener
from sphinx.highlighting import lexer_classes

# this package
from sphinx_toolbox.config import validate_config
from sphinx_toolbox.issues import IssueNode, depart_issue_node, visit_issue_node
from sphinx_toolbox.source import source_role
from sphinx_toolbox.testing import Sphinx, run_setup


class FakeBuilder(Builder):
	name = "FakeBuilder"


class FakeNodeVisitor(NodeVisitor):
	pass


class FakeDomain(Domain):
	name = "FakeDomain"


class FakeTransform(Transform):
	pass


class FakeLexer(Lexer):
	pass


def get_fake_lexer(*args) -> None:
	return None


def __setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup Sphinx Extension.

	:param app:

	:return:
	"""

	app.add_builder(FakeBuilder, override=True)

	app.add_config_value("source_link_target", "Sphinx", "env", types=[str])
	app.add_config_value("github_username", None, "env", types=[str])
	app.add_config_value("rebuild_true", None, True)
	app.add_config_value("rebuild_false", None, False)

	app.add_event("my-event")

	app.set_translator("my-translator", FakeNodeVisitor)

	app.add_node(IssueNode, html=(visit_issue_node, depart_issue_node))

	with pytest.raises(
			ValueError, match="node class 'IssueNode' is already registered, its visitors will be overridden"
			):
		app.add_node(IssueNode, html=(visit_issue_node, depart_issue_node))

	app.add_node(IssueNode, html=(visit_issue_node, depart_issue_node), override=True)

	# TODO: add_enumerable_node
	# TODO: add_directive

	app.add_role("source", source_role)

	with pytest.raises(ValueError, match="role 'source' is already registered, it will be overridden"):
		app.add_role("source", source_role)

	app.add_role("source", source_role, override=True)

	# TODO: add_generic_role

	app.add_domain(FakeDomain)
	app.add_domain(FakeDomain, override=True)

	app.add_role_to_domain("FakeDomain", "source", source_role)  # type: ignore
	app.add_role_to_domain("FakeDomain", "source", source_role, override=True)  # type: ignore

	# TODO: add_directive_to_domain
	# TODO: add_role_to_domain
	# TODO: add_index_to_domain
	# TODO: add_object_type
	# TODO: add_crossref_type

	app.add_transform(FakeTransform)
	app.add_post_transform(FakeTransform)

	app.add_latex_package("booktabs")
	app.add_latex_package("glossaries", options="acronyms")
	app.add_latex_package("chemformula", after_hyperref=True)

	app.add_lexer("my-lexer", FakeLexer)
	assert isinstance(FakeLexer(code='', language=''), Lexer)
	with pytest.raises(
			TypeError, match=r"app.add_lexer\(\) API changed; Please give lexer class instead instance"
			):
		app.add_lexer("my-lexer", FakeLexer(code='', language=''))

	# TODO: add_autodocumenter

	app.add_autodoc_attrgetter(FakeLexer, get_fake_lexer)

	app.add_source_suffix(".py", "python")
	app.add_source_suffix(".py", "python", override=True)

	# TODO: add_source_parser
	# TODO: add_env_collector

	app.add_html_theme("domdf_sphinx_theme", '.')

	# TODO: add_html_math_renderer

	app.connect("config-inited", validate_config, priority=850)

	return {"version": 12345, "parallel_read_safe": True}


def test_testing():
	setup_ret, directives, roles, additional_nodes, app = run_setup(__setup)  # type: ignore

	assert app.registry.builders["FakeBuilder"] == FakeBuilder

	assert app.config.values["source_link_target"] == ("Sphinx", "env", [str])
	assert app.config.values["github_username"] == (None, "env", [str])
	assert app.config.values["rebuild_true"] == (None, "env", ())
	assert app.config.values["rebuild_false"] == (None, '', ())

	assert app.events.events["my-event"] == ''
	assert app.registry.translators["my-translator"] is FakeNodeVisitor

	assert additional_nodes == {IssueNode}
	assert app.registry.translation_handlers == {"html": {"IssueNode": (visit_issue_node, depart_issue_node)}}

	assert roles == {"source": source_role}

	assert app.registry.domains["FakeDomain"] == FakeDomain
	assert app.registry.domain_roles.setdefault("FakeDomain", {})["source"] is source_role

	assert app.registry.transforms == [FakeTransform]
	assert app.registry.post_transforms == [FakeTransform]

	assert app.registry.latex_packages == [
			("booktabs", None),
			("glossaries", "acronyms"),
			]
	assert app.registry.latex_packages_after_hyperref == [("chemformula", None)]

	assert lexer_classes["my-lexer"] == FakeLexer
	assert app.registry.autodoc_attrgettrs[FakeLexer] is get_fake_lexer
	assert app.registry.source_suffix[".py"] == "python"
	assert app.html_themes == {"domdf_sphinx_theme": '.'}
	assert app.events.listeners["config-inited"] == [EventListener(id=0, handler=validate_config, priority=850)]
	assert setup_ret == {"version": 12345, "parallel_read_safe": True}

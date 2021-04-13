# stdlib
from typing import Set, Type

# 3rd party
import docutils.nodes
import pytest
from docutils import nodes
from sphinx.events import EventListener

# this package
import sphinx_toolbox
from sphinx_toolbox import github
from sphinx_toolbox.config import MissingOptionError
from sphinx_toolbox.github.issues import IssueNode, depart_issue_node, visit_issue_node
from sphinx_toolbox.github.repos_and_users import (
		GitHubObjectLinkNode,
		depart_github_object_link_node,
		repository_role,
		user_role,
		visit_github_object_link_node
		)
from sphinx_toolbox.testing import run_setup
from tests.common import AttrDict, error, info, severe, warning


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(github.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

	expected_additional_nodes: Set[Type[nodes.reference]] = {IssueNode, GitHubObjectLinkNode}
	assert additional_nodes == expected_additional_nodes
	assert app.registry.translation_handlers == {
			"html": {
					"IssueNode": (visit_issue_node, depart_issue_node),
					"GitHubObjectLinkNode": (visit_github_object_link_node, depart_github_object_link_node)
					}
			}

	# Moved to own setup function
	assert app.config.values["github_username"] == (None, "env", [str])
	assert app.config.values["github_repository"] == (None, "env", [str])

	assert app.events.listeners == {
			"config-inited": [EventListener(id=0, handler=github.validate_config, priority=850)],
			}

	assert directives == {}


def test_missing_options():

	config = AttrDict({
			"github_username": "octocat",
			"github_repository": None,
			})

	with pytest.raises(MissingOptionError, match="The 'github_repository' option is required."):
		github.validate_config('', config)  # type: ignore

	config = AttrDict({
			"github_username": None,
			"github_repository": "hello_world",
			})

	with pytest.raises(MissingOptionError, match="The 'github_username' option is required."):
		github.validate_config('', config)  # type: ignore


class FakeGitHubInliner:

	def __init__(self):
		app = AttrDict({"config": AttrDict()})
		env = AttrDict({"app": app})
		settings = AttrDict({"env": env})
		reporter = AttrDict({
				"info": info,
				"warning": warning,
				"error": error,
				"severe": severe,
				})
		self.document = AttrDict({"settings": settings, "reporter": reporter})


def test_user_role():
	nodes, messages = user_role('', '', "domdfcoding", 0, FakeGitHubInliner())  # type: ignore
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], GitHubObjectLinkNode)
	assert nodes[0].name == "@domdfcoding"
	assert nodes[0].url == "https://github.com/domdfcoding"


def test_user_role_with_text():
	nodes, messages = user_role('', '', "Checkout my user page <domdfcoding>", 0, FakeGitHubInliner())  # type: ignore
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], docutils.nodes.reference)
	assert nodes[0].rawsource == "Checkout my user page"
	assert nodes[0].attributes["refuri"] == "https://github.com/domdfcoding"


def test_repository_role():
	nodes, messages = repository_role('', '', "sphinx-toolbox/sphinx-toolbox", 0, FakeGitHubInliner())  # type: ignore
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], GitHubObjectLinkNode)
	assert nodes[0].name == "sphinx-toolbox/sphinx-toolbox"
	assert nodes[0].url == "https://github.com/sphinx-toolbox/sphinx-toolbox"


def test_repository_role_with_text():
	nodes, messages = repository_role('', '', "Checkout my repository <sphinx-toolbox/sphinx-toolbox>", 0, FakeGitHubInliner())  # type: ignore
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], docutils.nodes.reference)
	assert nodes[0].rawsource == "Checkout my repository"
	assert nodes[0].attributes["refuri"] == "https://github.com/sphinx-toolbox/sphinx-toolbox"

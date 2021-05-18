# stdlib
from typing import Set, Type

# 3rd party
import docutils.nodes
import pytest
from apeye.url import RequestsURL
from coincidence.params import count
from docutils import nodes
from docutils.utils import Reporter
from sphinx.events import EventListener

# this package
import sphinx_toolbox
from sphinx_toolbox import github
from sphinx_toolbox.config import MissingOptionError
from sphinx_toolbox.github.issues import (
		IssueNode,
		_depart_issue_node_latex,
		_visit_issue_node_latex,
		depart_issue_node,
		issue_role,
		pull_role,
		visit_issue_node
		)
from sphinx_toolbox.github.repos_and_users import (
		GitHubObjectLinkNode,
		_depart_github_object_link_node_latex,
		_visit_github_object_link_node_latex,
		depart_github_object_link_node,
		repository_role,
		user_role,
		visit_github_object_link_node
		)
from sphinx_toolbox.testing import run_setup
from sphinx_toolbox.utils import make_github_url
from tests.common import AttrDict, error_codes


class FakeGitHubInliner:

	def __init__(self):
		app = AttrDict({"config": AttrDict()})
		env = AttrDict({"app": app})
		settings = AttrDict({"env": env})
		reporter = Reporter('', 0, 100)

		self.document = AttrDict({"settings": settings, "reporter": reporter})


class FakePullInliner:

	def __init__(self, github_issues_url):
		config = AttrDict({"github_pull_url": RequestsURL(github_issues_url)})
		app = AttrDict({"config": config})
		env = AttrDict({"app": app})
		settings = AttrDict({"env": env})
		reporter = Reporter('', 0, 100)

		self.document = AttrDict({"settings": settings, "reporter": reporter})


class FakeIssueInliner:

	def __init__(self, github_issues_url):
		config = AttrDict({"github_issues_url": RequestsURL(github_issues_url)})
		app = AttrDict({"config": config})
		env = AttrDict({"app": app})
		settings = AttrDict({"env": env})
		reporter = Reporter('', 0, 100)

		self.document = AttrDict({"settings": settings, "reporter": reporter})


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


issues_repositories = pytest.mark.parametrize(
		"url, repository",
		[
				("https://github.com/domdfcoding/sphinx-toolbox/issues", "domdfcoding/sphinx-toolbox"),
				("https://github.com/pytest-dev/pytest/issues", "pytest-dev/pytest"),
				("https://github.com/tox-dev/tox/issues", "tox-dev/tox"),
				("https://github.com/python/cpython/issues", "python/cpython"),
				("https://github.com/psf/requests/issues", "psf/requests"),
				]
		)

pull_repositories = pytest.mark.parametrize(
		"url, repository",
		[
				("https://github.com/domdfcoding/sphinx-toolbox/pull", "domdfcoding/sphinx-toolbox"),
				("https://github.com/pytest-dev/pytest/pull", "pytest-dev/pytest"),
				("https://github.com/tox-dev/tox/pull", "tox-dev/tox"),
				("https://github.com/python/cpython/pull", "python/cpython"),
				("https://github.com/psf/requests/pull", "psf/requests"),
				]
		)


@pytest.mark.parametrize(
		"url",
		[
				"https://github.com/domdfcoding/sphinx-toolbox/issues",
				"https://github.com/pytest-dev/pytest/issues",
				"https://github.com/tox-dev/tox/issues",
				"https://github.com/python/cpython/issues",
				"https://github.com/psf/requests/issues",
				]
		)
@count(100)
def test_issue_role(count: int, url: str):
	issue_number = count
	nodes, messages = issue_role('', '', str(issue_number), 0, FakeIssueInliner(url))  # type: ignore
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip


@issues_repositories
@count(100, 0, 10)
def test_issue_role_with_repository(count: int, url: str, repository: str):
	issue_number = count
	nodes, messages = issue_role('', '', f"{issue_number} <{repository}>", 0, "Not a URL")  # type: ignore
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip


def test_issue_role_invalid_repository(capsys):
	url = "https://github.com/domdfcoding/sphinx-toolbox"

	nodes, messages = issue_role('', '', f"7 <foo>", 0, FakeIssueInliner(url))  # type: ignore
	assert capsys.readouterr().err == ":: (WARNING/2) Invalid repository 'foo' for issue #7.\n"

	issue_number = 7
	assert isinstance(nodes, list)
	assert nodes
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip

	assert isinstance(messages, list)
	assert messages
	assert isinstance(messages[0], docutils.nodes.system_message)
	assert messages[0].astext() == ":: (WARNING/2) Invalid repository 'foo' for issue #7."


@pytest.mark.parametrize(
		"url",
		[
				"https://github.com/domdfcoding/sphinx-toolbox/pull",
				"https://github.com/pytest-dev/pytest/pull",
				"https://github.com/tox-dev/tox/pull",
				"https://github.com/python/cpython/pull",
				"https://github.com/psf/requests/pull",
				]
		)
@count(100)
def test_pull_role(count: int, url: str):
	issue_number = count
	nodes, messages = pull_role('', '', str(issue_number), 0, FakePullInliner(url))  # type: ignore
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip


@pull_repositories
@count(100, 0, 10)
def test_pull_role_with_repository(count: int, url: str, repository: str):
	issue_number = count
	nodes, messages = pull_role('', '', f"{issue_number} <{repository}>", 0, "Not a URL")  # type: ignore
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip


def test_pull_role_invalid_repository(capsys):
	url = "https://github.com/domdfcoding/sphinx-toolbox"

	nodes, messages = pull_role('', '', f"7 <foo>", 0, FakePullInliner(url))  # type: ignore
	assert capsys.readouterr().err == ":: (WARNING/2) Invalid repository 'foo' for pull request #7.\n"

	issue_number = 7
	assert isinstance(nodes, list)
	assert nodes
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip

	assert isinstance(messages, list)
	assert messages
	assert isinstance(messages[0], docutils.nodes.system_message)
	assert messages[0].astext() == ":: (WARNING/2) Invalid repository 'foo' for pull request #7."


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


def test_repository_role_invalid(capsys):
	nodes, messages = repository_role(
		'',
		'',
		"Checkout my repository <sphinx-toolbox/sphinx-toolbox/default-values>",
		0,
		FakeGitHubInliner(),  # type: ignore
		)

	expected_stderr = ":: (WARNING/2) Invalid repository 'sphinx-toolbox/sphinx-toolbox/default-values'."
	assert capsys.readouterr().err == f"{expected_stderr}\n"

	assert isinstance(nodes, list)
	assert not nodes

	assert isinstance(messages, list)
	assert messages
	assert isinstance(messages[0], docutils.nodes.system_message)
	assert messages[0].astext() == expected_stderr


class FakeTranslator:

	def __init__(self):
		self.body = []

	def visit_reference(self, node):
		pass

	def depart_reference(self, node):
		pass


def test_visit_issue_node():
	node = IssueNode(7680, make_github_url("pytest-dev", "pytest") / "issues/7680")
	translator = FakeTranslator()

	assert not node.has_tooltip

	visit_issue_node(translator, node)  # type: ignore

	assert translator.body == ['<abbr title="Add --log-cli option">']
	assert node.has_tooltip


@error_codes
def test_visit_issue_node_errors(error_code, error_server):
	node = IssueNode(7680, error_server.url_for(f"/{error_code:d}"))
	translator = FakeTranslator()

	assert not node.has_tooltip

	with pytest.warns(UserWarning) as w:
		visit_issue_node(translator, node)  # type: ignore
	assert w[0].message.args[0] == "Issue/Pull Request #7680 not found."  # type: ignore

	assert translator.body == []
	assert not node.has_tooltip


def test_depart_issue_node():
	node = IssueNode(7680, make_github_url("pytest-dev", "pytest") / "issues/7680")
	translator = FakeTranslator()
	assert not node.has_tooltip

	depart_issue_node(translator, node)  # type: ignore

	assert translator.body == []

	node = IssueNode(7680, make_github_url("pytest-dev", "pytest") / "issues/7680")
	translator = FakeTranslator()
	node.has_tooltip = True

	depart_issue_node(translator, node)  # type: ignore

	assert translator.body == ["</abbr>"]


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(github.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

	expected_additional_nodes: Set[Type[nodes.reference]] = {IssueNode, GitHubObjectLinkNode}
	assert additional_nodes == expected_additional_nodes
	assert app.registry.translation_handlers == {
			"html": {
					"IssueNode": (visit_issue_node, depart_issue_node),
					"GitHubObjectLinkNode": (visit_github_object_link_node, depart_github_object_link_node)
					},
			"latex": {
					"IssueNode": (_visit_issue_node_latex, _depart_issue_node_latex),
					"GitHubObjectLinkNode": (
							_visit_github_object_link_node_latex,
							_depart_github_object_link_node_latex,
							)
					},
			}

	# Moved to own setup function
	assert app.config.values["github_username"] == (None, "env", [str])
	assert app.config.values["github_repository"] == (None, "env", [str])

	assert app.events.listeners == {
			"config-inited": [EventListener(id=0, handler=github.validate_config, priority=850)],
			}

	assert directives == {}

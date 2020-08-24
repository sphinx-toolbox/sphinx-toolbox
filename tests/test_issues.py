# 3rd party
import pytest
from apeye.url import RequestsURL
from domdf_python_tools.testing import count

# this package
from sphinx_toolbox import IssueNode, issue_role, pull_role
from tests.common import AttrDict


class FakePullInliner:

	def __init__(self, github_issues_url):
		config = AttrDict({"github_pull_url": RequestsURL(github_issues_url)})
		app = AttrDict({"config": config})
		env = AttrDict({"app": app})
		settings = AttrDict({"env": env})
		self.document = AttrDict({"settings": settings})


class FakeIssueInliner:

	def __init__(self, github_issues_url):
		config = AttrDict({"github_issues_url": RequestsURL(github_issues_url)})
		app = AttrDict({"config": config})
		env = AttrDict({"app": app})
		settings = AttrDict({"env": env})
		self.document = AttrDict({"settings": settings})


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
	nodes, messages = issue_role("", "", str(issue_number), 0, FakeIssueInliner(url))
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip


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


@issues_repositories
@count(100, 0, 10)
def test_issue_role_with_repository(count: int, url: str, repository: str):
	issue_number = count
	nodes, messages = issue_role("", "", f"{issue_number} <{repository}>", 0, "Not a URL")
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip


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
	nodes, messages = pull_role("", "", str(issue_number), 0, FakePullInliner(url))
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
	nodes, messages = pull_role("", "", f"{issue_number} <{repository}>", 0, "Not a URL")
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip


def test_pull_role_invalid_repository():
	url = "https://github.com/domdfcoding/sphinx-toolbox"

	with pytest.warns(UserWarning) as w:
		nodes, messages = pull_role("", "", f"7 <foo>", 0, FakePullInliner(url))
	assert len(w) == 1
	assert w[0].message.args[0] == "Invalid repository 'foo' for pull request #7."

	issue_number = 7
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip


def test_issue_role_invalid_repository():
	url = "https://github.com/domdfcoding/sphinx-toolbox"

	with pytest.warns(UserWarning) as w:
		nodes, messages = issue_role("", "", f"7 <foo>", 0, FakeIssueInliner(url))
	assert len(w) == 1
	assert w[0].message.args[0] == "Invalid repository 'foo' for issue #7."

	issue_number = 7
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip


# def test_visit_issue_node

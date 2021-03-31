# 3rd party
import pytest
from apeye.url import RequestsURL
from coincidence.params import count

# this package
import sphinx_toolbox
from sphinx_toolbox import issues
from sphinx_toolbox.issues import IssueNode, depart_issue_node, issue_role, pull_role, visit_issue_node
from sphinx_toolbox.testing import run_setup
from sphinx_toolbox.utils import make_github_url
from tests.common import AttrDict, error, error_codes, info, severe, warning


class FakePullInliner:

	def __init__(self, github_issues_url):
		config = AttrDict({"github_pull_url": RequestsURL(github_issues_url)})
		app = AttrDict({"config": config})
		env = AttrDict({"app": app})
		settings = AttrDict({"env": env})
		reporter = AttrDict({
				"info": info,
				"warning": warning,
				"error": error,
				"severe": severe,
				})
		self.document = AttrDict({"settings": settings, "reporter": reporter})


class FakeIssueInliner:

	def __init__(self, github_issues_url):
		config = AttrDict({"github_issues_url": RequestsURL(github_issues_url)})
		app = AttrDict({"config": config})
		env = AttrDict({"app": app})
		settings = AttrDict({"env": env})
		reporter = AttrDict({
				"info": info,
				"warning": warning,
				"error": error,
				"severe": severe,
				})
		self.document = AttrDict({"settings": settings, "reporter": reporter})


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
	nodes, messages = issue_role('', '', f"{issue_number} <{repository}>", 0, "Not a URL")  # type: ignore
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
	assert capsys.readouterr().out == "WARNING: Invalid repository 'foo' for pull request #7.\n"

	issue_number = 7
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
	assert capsys.readouterr().out == "WARNING: Invalid repository 'foo' for issue #7.\n"

	issue_number = 7
	assert isinstance(nodes, list)
	assert isinstance(messages, list)
	assert not messages
	assert isinstance(nodes[0], IssueNode)
	assert nodes[0].issue_url == f"{url}/{issue_number}"
	assert nodes[0].issue_number == issue_number
	assert not nodes[0].has_tooltip


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
	node = IssueNode(7680, error_server.url_for(f"/{error_code}"))
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


#
# @pytest.fixture()
# def rootdir():
# 	rdir = PathPlus(__file__).parent.absolute() / "github-doc-test"
# 	(rdir / "sphinx-test-github-root").maybe_make(parents=True)
# 	return rdir
#
#
# @pytest.fixture()
# def github_issues_app(app):
# 	return app
#
#
# @pytest.fixture()
# def issues_content(github_issues_app):
# 	github_issues_app.build(force_all=True)
# 	yield github_issues_app
#
#
# @pytest.fixture()
# def issues_page(issues_content, request) -> BeautifulSoup:
# 	pagename = request.param
# 	c = (issues_content.outdir / pagename).read_text()
#
# 	yield BeautifulSoup(c, "html5lib")
#
#
# @pytest.mark.parametrize("issues_page", ["index.html"], indirect=True)
# def test_output_github(issues_page: BeautifulSoup):
# 	# Make sure the page title is what you expect
# 	title = issues_page.find("h1").contents[0].strip()
# 	assert "sphinx-toolbox Demo" == title
#
# 	tag_count = 0
#
# 	for a_tag in issues_page.select("a.reference.external"):
# 		if a_tag["href"] == "https://github.com/domdfcoding/sphinx-toolbox/blob/master/sphinx_toolbox/config.py":
# 			if a_tag.contents[0] == "sphinx_toolbox/config.py":
# 				tag_count += 1
#
# 	assert tag_count == 1


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(issues.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}
	assert roles == {
			"issue": issue_role,
			"pr": pull_role,
			"pull": pull_role,
			}

	assert additional_nodes == {IssueNode}

	assert app.registry.translation_handlers == {"html": {"IssueNode": (visit_issue_node, depart_issue_node), }}

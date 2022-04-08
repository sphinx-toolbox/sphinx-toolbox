# stdlib
from types import SimpleNamespace

# 3rd party
import pytest

# this package
from sphinx_toolbox import sidebar_links
from sphinx_toolbox.testing import run_setup
from tests.common import AttrDict


class FakeBuildEnvironment(AttrDict):

	def __init__(self, tab_width: int):
		config = AttrDict({
				"docutils_tab_width": tab_width,
				"github_username": "octocat",
				"github_repository": "hello_world",
				"conda_channels": [],
				})
		app = AttrDict(extensions=[
				"sphinx_toolbox.installation",
				"sphinx_toolbox.github",
				])
		super().__init__({"config": config, "app": app})


def test_missing_extension():
	directive = SimpleNamespace()
	directive.env = SimpleNamespace()
	directive.env.app = AttrDict(extensions=["sphinx_toolbox.sidebar_links"])

	with pytest.raises(
			ValueError,
			match="The 'sphinx_toolbox.github' extension is required for the :github: option but it is not enabled!"
			):
		sidebar_links.SidebarLinksDirective.process_github_option(directive)  # type: ignore[arg-type]


def test_missing_username():
	directive = SimpleNamespace()
	directive.env = SimpleNamespace()
	directive.env.app = AttrDict(extensions=["sphinx_toolbox.sidebar_links", "sphinx_toolbox.github"])
	directive.env.config = AttrDict({"github_repository": "hello_world"})

	with pytest.raises(ValueError, match="'github_username' has not been set in 'conf.py'!"):
		sidebar_links.SidebarLinksDirective.process_github_option(directive)  # type: ignore[arg-type]


def test_missing_repo():
	directive = SimpleNamespace()
	directive.env = SimpleNamespace()
	directive.env.app = AttrDict(extensions=["sphinx_toolbox.sidebar_links", "sphinx_toolbox.github"])
	directive.env.config = AttrDict({"github_username": "octocat"})

	with pytest.raises(ValueError, match="'github_repository' has not been set in 'conf.py'!"):
		sidebar_links.SidebarLinksDirective.process_github_option(directive)  # type: ignore[arg-type]


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(sidebar_links.setup)

	assert app.events.listeners == {}

	assert directives == {"sidebar-links": sidebar_links.SidebarLinksDirective}
	assert app.registry.source_parsers == {}

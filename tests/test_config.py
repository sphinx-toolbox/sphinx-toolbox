# 3rd party
import pytest
from apeye.url import RequestsURL

# this package
from sphinx_toolbox import validate_config
from sphinx_toolbox.config import InvalidOptionError, MissingOptionError
from tests.common import AttrDict


def test_validate_config():
	config = AttrDict({
			"source_link_target": "Sphinx",
			"github_username": "domdfcoding",
			"github_repository": "sphinx-toolbox",
			})

	validate_config(None, config)

	assert config == {
			"source_link_target": "sphinx",
			"github_username": "domdfcoding",
			"github_repository": "sphinx-toolbox",
			"github_url": RequestsURL("https://github.com/domdfcoding/sphinx-toolbox"),
			"github_source_url": RequestsURL("https://github.com/domdfcoding/sphinx-toolbox/blob/master"),
			"github_issues_url": RequestsURL("https://github.com/domdfcoding/sphinx-toolbox/issues"),
			"github_pull_url": RequestsURL("https://github.com/domdfcoding/sphinx-toolbox/pull"),
			}

	config = AttrDict({
			"source_link_target": "Sphinx",
			"github_username": None,
			"github_repository": "sphinx-toolbox",
			})

	with pytest.raises(MissingOptionError, match="The 'github_username' option is required."):
		validate_config(None, config)

	config = AttrDict({
			"source_link_target": "Sphinx",
			"github_username": "domdfcoding",
			"github_repository": None,
			})

	with pytest.raises(MissingOptionError, match="The 'github_repository' option is required."):
		validate_config(None, config)

	config = AttrDict({
			"source_link_target": "bananas",
			"github_username": "domdfcoding",
			"github_repository": "sphinx-toolbox",
			})

	with pytest.raises(InvalidOptionError, match="Invalid value for 'source_link_target'."):
		validate_config(None, config)


@pytest.mark.parametrize(
		"target, expects",
		[
				("Sphinx", "sphinx"),
				("sphinx", "sphinx"),
				("GitHub", "github"),
				("Github", "github"),
				("github", "github"),
				]
		)
def test_source_link_target(target: str, expects: str):
	config = AttrDict({
			"source_link_target": target,
			"github_username": "domdfcoding",
			"github_repository": "sphinx-toolbox",
			})

	validate_config(None, config)

	assert config.source_link_target == expects

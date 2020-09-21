# 3rd party
import pytest
from sphinx.events import EventListener

# this package
import sphinx_toolbox
from sphinx_toolbox import github
from sphinx_toolbox.config import MissingOptionError
from sphinx_toolbox.testing import run_setup
from tests.common import AttrDict


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(github.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

	assert additional_nodes == set()
	assert app.registry.translation_handlers == {}

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

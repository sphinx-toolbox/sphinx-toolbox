# 3rd party
from sphinx.events import EventListener

# this package
import sphinx_toolbox
from sphinx_toolbox import github
from sphinx_toolbox.testing import run_setup


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

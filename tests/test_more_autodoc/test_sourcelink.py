# 3rd party
from sphinx.events import EventListener

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import sourcelink
from sphinx_toolbox.testing import run_setup
from tests.common import get_app_config_values


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(sourcelink.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {}
	assert roles == {}
	assert additional_nodes == set()

	_listener = [EventListener(id=0, handler=sourcelink.sourcelinks_process_docstring, priority=500)]
	assert app.events.listeners == {"autodoc-process-docstring": _listener}

	assert get_app_config_values(app.config.values["autodoc_show_sourcelink"]) == (False, "env", [bool])

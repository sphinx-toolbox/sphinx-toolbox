# this package
import sphinx_toolbox
from sphinx_toolbox import more_autodoc
from sphinx_toolbox.testing import run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(more_autodoc.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

	assert additional_nodes == set()
	assert app.registry.translation_handlers == {}
	assert app.events.listeners == {}
	assert directives == {}

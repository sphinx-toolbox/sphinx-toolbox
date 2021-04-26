# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import no_docstring
from sphinx_toolbox.testing import run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(no_docstring.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {}
	assert roles == {}
	assert additional_nodes == set()

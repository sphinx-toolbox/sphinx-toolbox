# 3rd party
from sphinx.ext.autodoc.directive import AutodocDirective

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import generic_bases
from sphinx_toolbox.testing import run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(generic_bases.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {"autoclass": AutodocDirective}
	assert roles == {}
	assert additional_nodes == set()

	assert app.registry.documenters["class"] == generic_bases.GenericBasesClassDocumenter

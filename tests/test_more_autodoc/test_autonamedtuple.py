# 3rd party
from sphinx.ext.autodoc.directive import AutodocDirective

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import autonamedtuple
from sphinx_toolbox.testing import run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(autonamedtuple.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {"autonamedtuple": AutodocDirective}
	assert roles == {}
	assert additional_nodes == set()

	assert "namedtuple" in app.registry.domains["py"].object_types
	assert "namedtuple" in app.registry.domain_directives["py"]
	assert "namedtuple" in app.registry.domain_roles["py"]

	assert app.registry.documenters["namedtuple"] == autonamedtuple.NamedTupleDocumenter

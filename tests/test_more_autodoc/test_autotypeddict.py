# 3rd party
from sphinx.ext.autodoc.directive import AutodocDirective

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import autotypeddict
from sphinx_toolbox.testing import run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(autotypeddict.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {"autotypeddict": AutodocDirective}
	assert roles == {}
	assert additional_nodes == set()

	assert "typeddict" in app.registry.domains["py"].object_types
	assert "typeddict" in app.registry.domain_directives["py"]
	assert "typeddict" in app.registry.domain_roles["py"]

	assert app.registry.documenters["typeddict"] == autotypeddict.TypedDictDocumenter

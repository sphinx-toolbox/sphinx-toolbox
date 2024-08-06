# 3rd party
from sphinx.ext.autodoc.directive import AutodocDirective

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import overloads
from sphinx_toolbox.testing import run_setup
from tests.common import get_app_config_values


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(overloads.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {"autofunction": AutodocDirective, "automethod": AutodocDirective}
	assert roles == {}
	assert additional_nodes == set()

	assert app.registry.documenters["function"] == overloads.FunctionDocumenter
	assert app.registry.documenters["method"] == overloads.MethodDocumenter

	assert get_app_config_values(app.config.values["overloads_location"])[:2] == ("signature", "env")

	assert get_app_config_values(app.config.values["overloads_location"])[2].candidates == (
			"top",
			"bottom",
			"signature",
			)

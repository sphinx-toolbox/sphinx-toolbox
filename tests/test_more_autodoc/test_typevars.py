# 3rd party
from sphinx.events import EventListener
from sphinx.ext.autodoc.directive import AutodocDirective

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import typevars
from sphinx_toolbox.testing import run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(typevars.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {"autotypevar": AutodocDirective}
	assert roles == {}
	assert additional_nodes == set()

	assert app.registry.documenters["typevar"] == typevars.TypeVarDocumenter

	assert app.events.listeners == {
			"config-inited": [EventListener(id=0, handler=typevars.validate_config, priority=850)],
			}

	assert app.config.values["no_unbound_typevars"] == (True, "env", [bool])

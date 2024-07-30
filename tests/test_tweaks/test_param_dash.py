# 3rd party
import sphinx.util.docfields

# this package
import sphinx_toolbox
from sphinx_toolbox.testing import run_setup
from sphinx_toolbox.tweaks import param_dash


def test_setup():
	original_make_field = sphinx.util.docfields.TypedField.make_field

	try:

		setup_ret, directives, roles, additional_nodes, app = run_setup(param_dash.setup)

		assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

		assert directives == {}
		assert additional_nodes == set()
		assert app.registry.translation_handlers == {}
		assert app.events.listeners == {}
	finally:
		sphinx.util.docfields.TypedField.make_field = original_make_field  # type: ignore[method-assign]

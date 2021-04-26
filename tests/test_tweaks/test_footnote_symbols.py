# 3rd party
from docutils.transforms.references import Footnotes

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.testing import run_setup
from sphinx_toolbox.tweaks import footnote_symbols


def test_setup():
	original_symbols = Footnotes.symbols

	try:

		setup_ret, directives, roles, additional_nodes, app = run_setup(footnote_symbols.setup)

		assert setup_ret == {"version": __version__, "parallel_read_safe": True}

		assert directives == {}
		assert additional_nodes == set()
		assert app.registry.translation_handlers == {}
		assert app.events.listeners == {}
		assert Footnotes.symbols == footnote_symbols.symbols

	finally:
		Footnotes.symbols = original_symbols

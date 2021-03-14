# 3rd party
from sphinx.events import EventListener

# this package
import sphinx_toolbox
from sphinx_toolbox.testing import run_setup
from sphinx_toolbox.tweaks import latex_toc


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(latex_toc.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

	assert additional_nodes == set()
	assert app.registry.translation_handlers == {}

	assert app.events.listeners == {
			"env-get-outdated": [EventListener(id=0, handler=latex_toc.purge_outdated, priority=500)],
			"config-inited": [EventListener(id=1, handler=latex_toc.configure, priority=500)],
			}

	assert directives == {"toctree": latex_toc.LatexTocTreeDirective}
	assert app.registry.translators["latex"] == latex_toc.LaTeXTranslator

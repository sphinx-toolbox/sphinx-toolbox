# 3rd party
from sphinx.events import EventListener

# this package
from sphinx_toolbox import latex
from sphinx_toolbox.testing import run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(latex.setup)

	assert app.events.listeners == {
			"config-inited": [EventListener(id=0, handler=latex.configure, priority=500)],
			}

	assert directives == {"samepage": latex.SamepageDirective}
	assert app.registry.source_parsers == {}
	assert app.registry.translation_handlers["latex"]["footnote"] == (latex.visit_footnote, latex.depart_footnote)

	assert app.registry.css_files == []
	assert app.registry.js_files == []

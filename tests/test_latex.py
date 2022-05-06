# 3rd party
from sphinx import addnodes
from sphinx.events import EventListener

# this package
from sphinx_toolbox import latex
from sphinx_toolbox.latex import succinct_seealso
from sphinx_toolbox.testing import run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(latex.setup)

	assert app.events.listeners == {
			"config-inited": [EventListener(id=0, handler=latex.configure, priority=500)],
			}

	assert directives == {
			"samepage": latex.SamepageDirective,
			"clearpage": latex.ClearPageDirective,
			"cleardoublepage": latex.ClearDoublePageDirective,
			}

	assert app.registry.source_parsers == {}
	assert app.registry.translation_handlers["latex"]["footnote"] == (latex.visit_footnote, latex.depart_footnote)

	assert app.registry.css_files == []
	assert app.registry.js_files == []


def test_setup_succinct_seealso():
	setup_ret, directives, roles, additional_nodes, app = run_setup(succinct_seealso.setup)

	assert additional_nodes == {addnodes.seealso}

	assert app.events.listeners == {}

	assert directives == {}

	assert app.registry.source_parsers == {}
	assert app.registry.translation_handlers["latex"]["seealso"] == (
			succinct_seealso.visit_seealso,
			succinct_seealso.depart_seealso,
			)

	assert app.registry.css_files == []
	assert app.registry.js_files == []

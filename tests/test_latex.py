# 3rd party
from docutils import nodes
from sphinx import addnodes
from sphinx.events import EventListener
from sphinx.writers.latex import LaTeXTranslator

# this package
import sphinx_toolbox
from sphinx_toolbox import latex
from sphinx_toolbox.latex import layout, succinct_seealso, toc
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


def test_setup_toc():
	setup_ret, directives, roles, additional_nodes, app = run_setup(toc.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

	assert additional_nodes == set()
	assert app.registry.translation_handlers == {}

	assert app.events.listeners == {
			"env-get-outdated": [EventListener(id=0, handler=toc.purge_outdated, priority=500)],
			"config-inited": [EventListener(id=1, handler=toc.configure, priority=500)],
			}

	assert directives == {"toctree": toc.LatexTocTreeDirective}
	assert app.registry.translators["latex"] == toc.LaTeXTranslator


def test_setup_layout():
	setup_ret, directives, roles, additional_nodes, app = run_setup(layout.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

	assert additional_nodes == {addnodes.desc, nodes.field_list, nodes.paragraph}
	assert app.registry.translation_handlers == {
			"latex": {
					"desc": (layout.visit_desc, LaTeXTranslator.depart_desc),
					"field_list": (layout.visit_field_list, layout.depart_field_list),
					"paragraph": (layout.visit_paragraph, LaTeXTranslator.depart_paragraph)
					}
			}

	assert app.events.listeners == {
			"config-inited": [EventListener(id=0, handler=layout.configure, priority=500)],
			}

	assert directives == {}

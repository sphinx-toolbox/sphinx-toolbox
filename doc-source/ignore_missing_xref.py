# 3rd party
from docutils import nodes
from sphinx.application import Sphinx
from sphinx.errors import NoUri


def handle_missing_xref(app: Sphinx, env, node: nodes.Node, contnode: nodes.Node) -> None:
	# Ignore missing reference warnings for the wheel_filename module
	if node.get("reftarget", '').startswith("docutils."):
		raise NoUri

	if node.get("reftarget", '').startswith("sphinx.ext.autodoc."):
		raise NoUri

	if node.get("reftarget", '').startswith("sphinx.ext.autosummary."):
		raise NoUri

	if node.get("reftarget", '').startswith("sphinx_toolbox._data_documenter."):
		# TODO: redirect
		raise NoUri

	if node.get("reftarget", '') in {
			"spam",
			"lobster",
			"foo",
			"typing_extensions",
			"bs4.BeautifulSoup",
			"pytest_regressions.file_regression.FileRegressionFixture",
			"sphinx_toolbox.patched_autosummary",
			"sphinx_toolbox.autodoc_augment_defaults",
			"sphinx_toolbox.autodoc_typehints",
			"sphinx_toolbox.autotypeddict",
			"sphinx_toolbox.autoprotocol",
			"sphinx_toolbox.utils._T",
			"sphinx_toolbox.testing.EventManager",  # TODO
			"sphinx.registry.SphinxComponentRegistry",
			"sphinx.config.Config",
			"sphinx.config.Config.latex_elements",
			"sphinx.util.docfields.TypedField",
			"sphinx.writers.html.HTMLTranslator",
			"sphinx.writers.html5.HTML5Translator",
			"sphinx.writers.latex.LaTeXTranslator",
			"sphinx.domains.python.PyXRefRole",
			"sphinx.domains.std.GenericObject",
			"sphinx.domains.changeset.VersionChange",
			"sphinx.directives.code.CodeBlock",
			"sphinx.roles.Abbreviation",
			"sphinx.roles.XRefRole",  # New 26 jun 24 with Sphinx 5.x and Python 3.8
			"autodoc.Documenter",  # TODO: why not sphinx.ext.autodoc.Documenter?
			}:
		raise NoUri

	if node.get("reftarget", '').startswith("consolekit.terminal_colours.Fore."):
		raise NoUri


def setup(app: Sphinx):
	app.connect("missing-reference", handle_missing_xref, priority=950)

# 3rd party
from coincidence.regressions import AdvancedFileRegressionFixture
from sphinx.ext.autodoc.directive import AutodocDirective

# this package
from sphinx_toolbox import __version__, more_autosummary
from sphinx_toolbox.testing import run_setup


def test_setup(advanced_file_regression: AdvancedFileRegressionFixture):
	setup_ret, directives, roles, additional_nodes, app = run_setup(more_autosummary.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {
			"autosummary": more_autosummary.PatchedAutosummary,
			"autoclass": AutodocDirective,
			"automodule": AutodocDirective,
			}

	assert app.registry.documenters["module"] == more_autosummary.PatchedAutoSummModuleDocumenter
	assert app.registry.documenters["class"] == more_autosummary.PatchedAutoSummClassDocumenter

	assert not roles
	assert not additional_nodes

	assert app.config.values["autodocsumm_member_order"][:2] == (
			"alphabetical",
			"env",
			)

	assert app.config.values["autodocsumm_member_order"][2].candidates == (
			"alphabetic", "alphabetical", "bysource"
			)

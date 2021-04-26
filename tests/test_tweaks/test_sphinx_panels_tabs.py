# 3rd party
from coincidence.regressions import AdvancedFileRegressionFixture
from sphinx.events import EventListener

# this package
import sphinx_toolbox
from sphinx_toolbox.testing import check_asset_copy, run_setup
from sphinx_toolbox.tweaks import sphinx_panels_tabs


def test_copy_asset_files(tmp_pathplus, advanced_file_regression: AdvancedFileRegressionFixture):
	check_asset_copy(
			sphinx_panels_tabs.copy_asset_files,
			"_static/css/tabs_customise.css",
			file_regression=advanced_file_regression,
			)


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(sphinx_panels_tabs.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

	assert directives == {}
	assert additional_nodes == set()

	assert app.registry.translation_handlers == {
			"html": {"container": (sphinx_panels_tabs.visit_container, sphinx_panels_tabs.depart_container)}
			}

	assert app.events.listeners == {
			"build-finished": [EventListener(id=0, handler=sphinx_panels_tabs.copy_asset_files, priority=500)],
			}

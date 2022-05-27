# 3rd party
from coincidence.regressions import AdvancedFileRegressionFixture
from domdf_python_tools.paths import PathPlus
from sphinx.events import EventListener

# this package
import sphinx_toolbox
from sphinx_toolbox import _css
from sphinx_toolbox.testing import check_asset_copy, run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(_css.setup)

	assert setup_ret == {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

	assert additional_nodes == set()
	assert app.registry.translation_handlers == {}
	assert app.events.listeners == {"build-finished": [EventListener(0, _css.copy_asset_files, 500)]}
	assert app.registry.css_files == [("css/sphinx-toolbox.css", {})]


def test_copy_asset_files(tmp_pathplus: PathPlus, advanced_file_regression: AdvancedFileRegressionFixture):
	check_asset_copy(
			_css.copy_asset_files,
			"_static/css/sphinx-toolbox.css",
			file_regression=advanced_file_regression,
			)

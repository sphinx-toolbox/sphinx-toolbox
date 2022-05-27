# 3rd party
from coincidence.regressions import AdvancedFileRegressionFixture
from domdf_python_tools.paths import PathPlus
from sphinx.events import EventListener

# this package
from sphinx_toolbox import __version__, code
from sphinx_toolbox.testing import check_asset_copy, run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(code.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {
			"code-block": code.CodeBlock,
			"sourcecode": code.CodeBlock,
			"code-cell": code.CodeCell,
			"output-cell": code.OutputCell,
			}

	assert not roles

	assert additional_nodes == {code.Prompt}

	assert app.events.listeners == {
			"build-finished": [EventListener(id=1, handler=code.copy_asset_files, priority=500)],
			"config-inited": [EventListener(id=0, handler=code.configure, priority=500)],
			}


def test_copy_asset_files(tmp_pathplus: PathPlus, advanced_file_regression: AdvancedFileRegressionFixture):
	check_asset_copy(
			code.copy_asset_files,
			"_static/sphinx-toolbox-code.css",
			file_regression=advanced_file_regression,
			)

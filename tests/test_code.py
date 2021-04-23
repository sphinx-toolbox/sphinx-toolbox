# 3rd party
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from sphinx_toolbox import code
from sphinx_toolbox.testing import check_asset_copy, run_setup


def test_setup(file_regression: FileRegressionFixture):
	setup_ret, directives, roles, additional_nodes, app = run_setup(code.setup)

	assert directives == {
			"code-block": code.CodeBlock,
			"sourcecode": code.CodeBlock,
			"code-cell": code.CodeCell,
			"output-cell": code.OutputCell,
			}


def test_copy_asset_files(tmp_pathplus, file_regression: FileRegressionFixture):
	check_asset_copy(
			code.copy_asset_files,
			"_static/sphinx-toolbox-code.css",
			file_regression=file_regression,
			)

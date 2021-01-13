from types import SimpleNamespace

from domdf_python_tools.testing import check_file_output
from pytest_regressions.file_regression import FileRegressionFixture

from sphinx_toolbox.tweaks.sphinx_panels_tabs import copy_assets


def test_copy_assets(tmp_pathplus, file_regression: FileRegressionFixture):

	fake_app = SimpleNamespace()
	fake_app.builder = SimpleNamespace()
	fake_app.builder.outdir = tmp_pathplus

	copy_assets(fake_app, None)  # type: ignore

	check_file_output(
			tmp_pathplus / "_static" / "css" / "tabs_customise.css",
			file_regression,
			)

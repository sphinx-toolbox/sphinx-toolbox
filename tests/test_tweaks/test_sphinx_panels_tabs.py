# stdlib
from types import SimpleNamespace

# 3rd party
from coincidence.regressions import AdvancedFileRegressionFixture

# this package
from sphinx_toolbox.tweaks.sphinx_panels_tabs import copy_assets


def test_copy_assets(tmp_pathplus, advanced_file_regression: AdvancedFileRegressionFixture):

	fake_app = SimpleNamespace()
	fake_app.builder = SimpleNamespace()
	fake_app.builder.outdir = tmp_pathplus

	copy_assets(fake_app, None)  # type: ignore

	advanced_file_regression.check_file(tmp_pathplus / "_static" / "css" / "tabs_customise.css")

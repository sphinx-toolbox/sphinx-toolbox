# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus
from sphinx.application import Sphinx
from sphinx.ext.autodoc.directive import AutodocDirective

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import overloads
from sphinx_toolbox.testing import run_setup
from tests.common import get_app_config_values


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(overloads.setup, call_config_events=True)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {"autofunction": AutodocDirective, "automethod": AutodocDirective}
	assert roles == {}
	assert additional_nodes == set()

	assert app.registry.documenters["function"] == overloads.FunctionDocumenter
	assert app.registry.documenters["method"] == overloads.MethodDocumenter

	config_values = get_app_config_values(app.config.values["overloads_location"])
	assert config_values[:2] == ("signature", "env")

	assert sorted(config_values[2].candidates) == [
			"bottom",
			"signature",
			"top",
			]


@pytest.fixture()
def doc_root(tmp_pathplus: PathPlus) -> None:
	doc_root = tmp_pathplus.parent / "test-overloads-location"
	doc_root.maybe_make()

	(doc_root / "conf.py").write_lines([
			"extensions = ['sphinx.ext.autodoc', 'sphinx_toolbox.more_autodoc.overloads']",
			])
	(doc_root / "index.rst").write_lines([
			".. autofunction:: tests.test_output.overloads_demo.serde",
			])


@pytest.mark.usefixtures("doc_root")
@pytest.mark.parametrize(
		"location",
		[
				pytest.param(
						"top",
						marks=pytest.mark.sphinx(
								"html",
								testroot="test-overloads-location",
								confoverrides={"overloads_location": "top"},
								),
						),
				pytest.param(
						"bottom",
						marks=pytest.mark.sphinx(
								"html",
								testroot="test-overloads-location",
								confoverrides={"overloads_location": "bottom"},
								),
						),
				],
		)
def test_overloads_location_body(app: Sphinx, location: str):
	# https://github.com/sphinx-toolbox/sphinx-toolbox/issues/225
	# Overloads in the body need ``docutils_tab_width``, from ``sphinx_toolbox.tweaks.tabsize``.
	assert app.config.overloads_location == location

	app.build()

	output = (PathPlus(app.outdir) / "index.html").read_text()
	assert "Overloads" in output

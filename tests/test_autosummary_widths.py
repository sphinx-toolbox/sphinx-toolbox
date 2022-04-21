# stdlib
import shutil
from typing import cast

# 3rd party
import pytest
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from sphinx.application import Sphinx
from sphinx.builders import Builder

# this package
from sphinx_toolbox.testing import LaTeXRegressionFixture


@pytest.fixture()
def doc_root(tmp_pathplus: PathPlus):
	doc_root = tmp_pathplus.parent / "test-autosummary-widths"
	doc_root.maybe_make()
	test_root = PathPlus(__file__).parent / "test-root-aw"

	shutil.copy2(test_root / "conf.py", doc_root / "conf.py")
	shutil.copy2(test_root / "index.rst", doc_root / "index.rst")


@pytest.mark.usefixtures("doc_root")
@pytest.mark.sphinx("latex", testroot="test-autosummary-widths")
def test_latex_output(
		app: Sphinx,
		latex_regression: LaTeXRegressionFixture,
		):

	assert cast(Builder, app.builder).name.lower() == "latex"

	app.build()

	output_file = PathPlus(app.outdir) / "python.tex"

	latex_regression.check(StringList(output_file.read_lines()), jinja2=True)

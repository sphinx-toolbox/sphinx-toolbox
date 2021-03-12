# stdlib
import re
import sys

# 3rd party
import pytest
from bs4 import BeautifulSoup  # type: ignore
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.testing import check_file_regression, min_version, only_version
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from sphinx_toolbox.testing import HTMLRegressionFixture


def test_build_example(testing_app):
	testing_app.build()
	testing_app.build()


@pytest.mark.parametrize("page", ["shields.html"], indirect=True)
def test_shields_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - Shields" == title

	selector_string = "div.body div#sphinx-toolbox-demo-shields"
	assert list(filter(lambda a: a != '\n', page.select(selector_string)[0].contents))[1:]


@pytest.mark.parametrize("page", ["code-block.html"], indirect=True)
def test_code_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - Code" == title

	assert list(filter(lambda a: a != '\n', page.select("div.body div#sphinx-toolbox-demo-code")[0].contents))[1:]


@pytest.mark.parametrize("page", ["example.html"], indirect=True)
def test_example_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - reST Example" == title

	selector_string = "div.body div#sphinx-toolbox-demo-rest-example"
	body = list(filter(lambda a: a != '\n', page.select(selector_string)[0].contents))[1:]

	assert len(body) == 4

	assert body[0].name == 'p'
	assert body[0]["id"] == "example-0"
	assert body[0].contents == []

	assert body[1].name == "div"
	assert body[1]["class"] == ["highlight-rest", "notranslate"]
	assert body[1].contents[0].name == "div"
	assert body[1].contents[0]["class"] == ["highlight"]

	assert body[2].name == "div"
	assert body[2]["class"] == ["highlight-python", "notranslate"]

	assert body[3].name == 'p'
	assert body[3].contents == []


@pytest.mark.parametrize("page", ["installation.html"], indirect=True)
def test_installation_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - Installation" == title

	selector_string = "div.body div#sphinx-toolbox-demo-installation"
	assert list(filter(lambda a: a != '\n', page.select(selector_string)[0].contents))[1:]


@pytest.mark.parametrize(
		"page",
		[
				"assets.html",
				"augment-defaults.html",
				"autodoc-ellipsis.html",
				"autonamedtuple.html",
				"autonamedtuple_pep563.html",
				"autoprotocol.html",
				"autotypeddict.html",
				"code-block.html",
				"confval.html",
				"decorators.html",
				"example.html",
				"flake8.html",
				"formatting.html",
				"installation.html",
				"no_docstring.html",
				"overloads.html",
				"pre-commit.html",
				"regex.html",
				"shields.html",
				"sourcelink.html",
				"typevars.html",
				"variables.html",
				"wikipedia.html",
				pytest.param(
						"instancevar.html",
						marks=pytest.mark.skipif(
								condition=sys.version_info < (3, 7),
								reason="Output differs on Python 3.6",
								),
						),
				pytest.param(
						"generic_bases.html",
						marks=only_version(3.6, reason="Output differs on Python 3.6"),
						id="generic_bases_36"
						),
				pytest.param(
						"generic_bases.html",
						marks=only_version(3.7, reason="Output differs on Python 3.7"),
						id="generic_bases_37"
						),
				pytest.param(
						"generic_bases.html",
						marks=min_version(3.8, reason="Output differs on Python 3.8+"),
						id="generic_bases"
						),
				pytest.param(
						"genericalias.html",
						marks=min_version(3.7, reason="Output differs on Python 3.6"),
						id="genericalias"
						),
				],
		indirect=True
		)
def test_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	"""
	Parametrize new files here rather than as their own function.
	"""

	html_regression.check(page)


@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output(app, file_regression: FileRegressionFixture):

	assert app.builder.name.lower() == "latex"
	app.build()

	output_file = PathPlus(app.outdir / "python.tex")
	content = StringList(output_file.read_lines())
	check_file_regression(
			re.sub(r"\\date{.*}", r"\\date{Mar 11, 2021}", str(content)),
			file_regression,
			extension=".tex",
			)

# stdlib
import sys

# 3rd party
import pytest
from bs4 import BeautifulSoup  # type: ignore

# this package
from sphinx_toolbox.testing import HTMLRegressionFixture


def test_build_example(testing_app):
	testing_app.build()
	testing_app.build()


@pytest.mark.parametrize("page", ["confval.html"], indirect=True)
def test_confval_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "Confval" == title

	# Testing the actual content with check_html_regression
	html_regression.check(page)


@pytest.mark.parametrize("page", ["shields.html"], indirect=True)
def test_shields_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - Shields" == title

	selector_string = "div.body div#sphinx-toolbox-demo-shields"
	assert list(filter(lambda a: a != '\n', page.select(selector_string)[0].contents))[1:]

	# Testing the actual content with check_html_regression
	html_regression.check(page)


@pytest.mark.parametrize("page", ["code-block.html"], indirect=True)
def test_code_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - Code" == title

	assert list(filter(lambda a: a != '\n', page.select("div.body div#sphinx-toolbox-demo-code")[0].contents))[1:]

	# Testing the actual content with check_html_regression
	html_regression.check(page)


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

	# Testing the actual content with check_html_regression
	html_regression.check(page)


@pytest.mark.parametrize("page", ["installation.html"], indirect=True)
def test_installation_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - Installation" == title

	selector_string = "div.body div#sphinx-toolbox-demo-installation"
	assert list(filter(lambda a: a != '\n', page.select(selector_string)[0].contents))[1:]

	# Testing the actual content with check_html_regression
	html_regression.check(page)


@pytest.mark.parametrize("page", ["augment-defaults.html"], indirect=True)
def test_augment_defaults_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "Autodoc Augment Defaults" == title

	# Testing the actual content with check_html_regression
	html_regression.check(page)


@pytest.mark.parametrize("page", ["wikipedia.html"], indirect=True)
def test_wikipedia_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - Wikipedia" == title

	# Testing the actual content with check_html_regression
	html_regression.check(page)


@pytest.mark.parametrize("page", ["formatting.html"], indirect=True)
def test_formatting_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - Formatting" == title

	# Testing the actual content with check_html_regression
	html_regression.check(page)


@pytest.mark.parametrize(
		"page",
		[
				"assets.html",
				"autotypeddict.html",
				"autonamedtuple.html",
				"autodoc-ellipsis.html",
				"variables.html",
				"decorators.html",
				"no_docstring.html",
				"sourcelink.html",
				"regex.html",
				"autoprotocol.html",
				"typevars.html",
				"overloads.html",
				"pre-commit.html",
				"flake8.html",
				pytest.param(
						"instancevar.html",
						marks=pytest.mark.skipif(
								condition=sys.version_info < (3, 7),
								reason="Output differs on Python 3.6",
								),
						),
				],
		indirect=True
		)
def test_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	"""
	Parametrize new files here rather than as their own function.
	"""

	html_regression.check(page)


@pytest.mark.skipif(condition=sys.version_info < (3, 7), reason="Output differs for Py36")
@pytest.mark.parametrize("page", ["genericalias.html"], indirect=True)
def test_genericalias_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	html_regression.check(page)


@pytest.mark.skipif(condition=sys.version_info[:2] != (3, 6), reason="Output differs for Py36")
@pytest.mark.parametrize("page", ["generic_bases.html"], indirect=True)
def test_generic_bases_html_output_36(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	html_regression.check(page)


@pytest.mark.skipif(condition=sys.version_info[:2] != (3, 7), reason="Output differs for Py37")
@pytest.mark.parametrize("page", ["generic_bases.html"], indirect=True)
def test_generic_bases_html_output_37(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	html_regression.check(page)


@pytest.mark.skipif(condition=sys.version_info <= (3, 8), reason="Output differs for Py38")
@pytest.mark.parametrize("page", ["generic_bases.html"], indirect=True)
def test_generic_bases_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	html_regression.check(page)

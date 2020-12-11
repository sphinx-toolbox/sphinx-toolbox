# 3rd party
import pytest
from bs4 import BeautifulSoup  # type: ignore
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from sphinx_toolbox.testing import check_html_regression


def test_build_example(inline_tabs_app):
	inline_tabs_app.build()
	inline_tabs_app.build()


@pytest.mark.parametrize("inline_tabs_page", ["index.html"], indirect=True)
def test_installation_html_output(inline_tabs_page: BeautifulSoup, file_regression: FileRegressionFixture):
	# Make sure the page title is what you expect
	title = inline_tabs_page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - Installation" == title

	selector_string = "div.body div#sphinx-toolbox-demo-installation"
	assert list(filter(lambda a: a != '\n', inline_tabs_page.select(selector_string)[0].contents))[1:]

	# Testing the actual content with check_html_regression
	check_html_regression(inline_tabs_page, file_regression)

# 3rd party
import pytest
from bs4 import BeautifulSoup  # type: ignore[import-untyped]
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.testing import HTMLRegressionFixture


def test_build_sphinx(sphinx_src_app: Sphinx):
	# app is a Sphinx application object for default sphinx project (`tests/doc-test/sphinx-test-github-root`).
	sphinx_src_app.build()
	sphinx_src_app.build()


@pytest.mark.usefixtures("docutils_17_compat")
@pytest.mark.parametrize("sphinx_source_page", ["index.html"], indirect=True)
def test_output_sphinx(sphinx_source_page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = sphinx_source_page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - Sphinx source" == title

	tag_count = 0

	for a_tag in sphinx_source_page.select("a.reference.internal"):
		if tag_count == 0:
			if a_tag.contents[0] == "sphinx_toolbox/config.py":
				assert a_tag["href"] == "_modules/sphinx_toolbox/config.html#sphinx_toolbox/config.py"
		elif tag_count == 1:
			if a_tag.contents[0] == "source code":
				assert a_tag["href"] == "_modules/sphinx_toolbox/config.html#sphinx_toolbox/config.py"
		tag_count += 1

	assert tag_count == 4

	html_regression.check(sphinx_source_page, jinja2=True)

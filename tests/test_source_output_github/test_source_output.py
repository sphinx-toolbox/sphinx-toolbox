# stdlib
from typing import Optional, cast

# 3rd party
import pytest
from bs4 import BeautifulSoup, Tag
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.testing import HTMLRegressionFixture


def test_build_github(gh_src_app: Sphinx):
	# app is a Sphinx application object for default sphinx project (`tests/doc-test/sphinx-test-github-root`).
	gh_src_app.build()
	gh_src_app.build()


@pytest.mark.usefixtures("docutils_17_compat")
@pytest.mark.parametrize("github_source_page", ["index.html"], indirect=True)
def test_output_github(github_source_page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	h1 = cast(Optional[Tag], github_source_page.find("h1"))
	assert h1 is not None
	title = cast(str, h1.contents[0]).strip()
	assert "sphinx-toolbox Demo" == title

	tag_count = 0

	for a_tag in github_source_page.select("a.reference.external"):
		if tag_count == 0:
			if a_tag.contents[0] == "sphinx_toolbox/config.py":
				assert a_tag[
						"href"
						] == "https://github.com/sphinx-toolbox/sphinx-toolbox/blob/master/sphinx_toolbox/config.py"
		elif tag_count == 1:
			if a_tag.contents[0] == "source code":
				assert a_tag[
						"href"
						] == "https://github.com/sphinx-toolbox/sphinx-toolbox/blob/master/sphinx_toolbox/config.py"
		tag_count += 1

	assert tag_count == 2

	html_regression.check(github_source_page, jinja2=True)

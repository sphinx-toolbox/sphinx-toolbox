# 3rd party
import pytest
from bs4 import BeautifulSoup  # type: ignore

# this package
from sphinx_toolbox.testing import HTMLRegressionFixture


def test_build_github(gh_src_app):
	# app is a Sphinx application object for default sphinx project (`tests/doc-test/sphinx-test-github-root`).
	gh_src_app.build()
	gh_src_app.build()


@pytest.mark.parametrize("github_source_page", ["index.html"], indirect=True)
def test_output_github(github_source_page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = github_source_page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - GitHub Issues" == title

	links = github_source_page.select('p')
	assert len(links) == 5

	assert links[1] == links[2]

	assert links[0].abbr["title"] == "Example Issue"  # check the abbr tag
	assert links[0].abbr.a["class"] == ["reference", "external"]  # check the a tag's class
	assert links[0].abbr.a["href"
							] == "https://github.com/domdfcoding/sphinx-toolbox/issues/1"  # check the a tag's href
	assert links[0].abbr.a.contents[0] == "#1"  # check the body

	assert [str(x) for x in links] == [
			'<p><abbr title="Example Issue"><a class="reference external" '
			'href="https://github.com/domdfcoding/sphinx-toolbox/issues/1">#1</a></abbr></p>',
			'<p><abbr title="Example Pull Request"><a class="reference external" '
			'href="https://github.com/domdfcoding/sphinx-toolbox/pull/2">#2</a></abbr></p>',
			'<p><abbr title="Example Pull Request"><a class="reference external" '
			'href="https://github.com/domdfcoding/sphinx-toolbox/pull/2">#2</a></abbr></p>',
			'<p><abbr title="Add --log-cli option"><a class="reference external" '
			'href="https://github.com/pytest-dev/pytest/issues/7680">#7680</a></abbr></p>',
			'<p><abbr title="RFC: python: skip work pytest_pycollect_makeitem work on certain names"><a '
			'class="reference external" href="https://github.com/pytest-dev/pytest/issues/7671">#7671</a></abbr></p>',
			]

	html_regression.check(github_source_page)

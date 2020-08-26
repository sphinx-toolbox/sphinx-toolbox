# 3rd party
import pytest
from bs4 import BeautifulSoup


def test_build_github(gh_src_app):
	# app is a Sphinx application object for default sphinx project (`tests/doc-test/sphinx-test-github-root`).
	gh_src_app.build()


@pytest.mark.parametrize("github_source_page", ["index.html"], indirect=True)
def test_output_github(github_source_page: BeautifulSoup):
	# Make sure the page title is what you expect
	title = github_source_page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo" == title

	tag_count = 0

	for a_tag in github_source_page.select("a.reference.external"):
		if tag_count == 0:
			if a_tag.contents[0] == "sphinx_toolbox/config.py":
				assert a_tag[
						"href"
						] == "https://github.com/domdfcoding/sphinx-toolbox/blob/master/sphinx_toolbox/config.py"
		elif tag_count == 1:
			if a_tag.contents[0] == "source code":
				assert a_tag[
						"href"
						] == "https://github.com/domdfcoding/sphinx-toolbox/blob/master/sphinx_toolbox/config.py"
		tag_count += 1

	assert tag_count == 2

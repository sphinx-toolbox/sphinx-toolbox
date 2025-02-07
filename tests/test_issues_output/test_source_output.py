# stdlib
from typing import Dict, List, Optional, Union, cast

# 3rd party
import pytest
from _pytest.mark import ParameterSet
from bs4 import BeautifulSoup, Tag
from coincidence.selectors import min_version, only_version
from domdf_python_tools.paths import PathPlus
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
	assert "sphinx-toolbox Demo - GitHub Issues" == title

	links = cast(List[Tag], github_source_page.select('p'))
	assert len(links) == 10

	assert links[1] == links[2]

	assert links[0].abbr["title"] == "Example Issue"  # type: ignore[index]  # check the abbr tag

	# check the a tag's class
	expected_classes = ["reference", "external"]
	assert links[0].abbr.a["class"] == expected_classes  # type: ignore[index,union-attr]

	expected_href = "https://github.com/sphinx-toolbox/sphinx-toolbox/issues/1"
	assert links[0].abbr.a["href"] == expected_href  # type: ignore[index,union-attr]  # check the a tag's href
	assert links[0].abbr.a.contents[0] == "#1"  # type: ignore[union-attr]    # check the body

	assert [str(x) for x in links] == [
			'<p><abbr title="Example Issue"><a class="reference external" '
			'href="https://github.com/sphinx-toolbox/sphinx-toolbox/issues/1">#1</a></abbr></p>',
			'<p><abbr title="Example Pull Request"><a class="reference external" '
			'href="https://github.com/sphinx-toolbox/sphinx-toolbox/pull/2">#2</a></abbr></p>',
			'<p><abbr title="Example Pull Request"><a class="reference external" '
			'href="https://github.com/sphinx-toolbox/sphinx-toolbox/pull/2">#2</a></abbr></p>',
			'<p><abbr title="Add --log-cli option"><a class="reference external" '
			'href="https://github.com/pytest-dev/pytest/issues/7680">pytest-dev/pytest#7680</a></abbr></p>',
			'<p><abbr title="RFC: python: skip work pytest_pycollect_makeitem work on certain names"><a '
			'class="reference external" href="https://github.com/pytest-dev/pytest/issues/7671">pytest-dev/pytest#7671</a></abbr></p>',
			'<p><a class="reference external" '
			'href="https://github.com/sphinx-toolbox/sphinx-toolbox/blob/master/sphinx_toolbox/source.py">sphinx_toolbox/source.py</a></p>',
			'<p><a class="reference external" '
			'href="https://github.com/sphinx-toolbox/sphinx-toolbox/blob/master/sphinx_toolbox/more_autodoc/__init__.py">sphinx_toolbox/more_autodoc/__init__.py</a></p>',
			'<p>Issue with code in its title: <abbr title="Unable to install latest '
			'version of flake8 and Sphinx together"><a class="reference external" '
			'href="https://github.com/sphinx-doc/sphinx/issues/10241">sphinx-doc/sphinx#10241</a></abbr>.</p>',
			'<p>Issue with code in the beginning of the title: <abbr '
			'title=\'autodoc_typehints = "description" causes autoclass to put a return '
			'type\'><a class="reference external" '
			'href="https://github.com/sphinx-doc/sphinx/issues/9575">sphinx-doc/sphinx#9575</a></abbr>.</p>',
			'<p>Issue with HTML entities in title: <abbr title="RFE: please provide '
			'support for jinja2 &gt;= 3.1"><a class="reference external" '
			'href="https://github.com/sphinx-toolbox/toctree_plus/issues/56">sphinx-toolbox/toctree_plus#56</a></abbr>.</p>',
			]

	html_regression.check(github_source_page, jinja2=True)


# The following is in here because it needs to run with different options to tests/test_output

pages_to_check: List[Union[str, ParameterSet]] = [
		"autoprotocol.html",
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
		]


@pytest.mark.usefixtures("docutils_17_compat")
def test_html_output(gh_src_app: Sphinx, html_regression: HTMLRegressionFixture):
	"""
	Parametrize new files here rather than as their own function.
	"""

	gh_src_app.build(force_all=True)

	caught_exceptions: List[BaseException] = []

	for page in pages_to_check:
		if isinstance(page, str):
			page = pytest.param(page, id=page)

		pagename: str = page.values[0]  # type: ignore[assignment]
		page_id: str = page.id or pagename
		for mark in page.marks:
			if mark.kwargs.get("condition", False):
				if "reason" in mark.kwargs:
					print(f"Skipping {page_id!r}: {mark.kwargs['reason']}")

					break
				else:
					print(f"Skipping {page_id!r}")
					break
		else:
			print(f"Checking output for {page_id}")
			page_id = page_id.replace('.', '_').replace('-', '_')
			content = (PathPlus(gh_src_app.outdir) / pagename).read_text()

			soup = BeautifulSoup(content, "html5lib")

			for meta in cast(List[Dict], soup.find_all("meta")):
				if meta.get("content", '') == "width=device-width, initial-scale=0.9, maximum-scale=0.9":
					meta.extract()  # type: ignore[attr-defined]

			try:
				html_regression.check(
						soup,
						extension=f"_{page_id}_.html",
						jinja2=True,
						)
			except BaseException as e:
				caught_exceptions.append(e)

		continue

	print(caught_exceptions)

	for exception in caught_exceptions:
		raise exception

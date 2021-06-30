# stdlib
import re
import sys
from typing import List, Union

# 3rd party
import pytest
from _pytest.mark import ParameterSet
from bs4 import BeautifulSoup  # type: ignore
from coincidence.regressions import AdvancedFileRegressionFixture
from coincidence.selectors import min_version, only_version
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList

# this package
from sphinx_toolbox.latex import better_header_layout
from sphinx_toolbox.testing import HTMLRegressionFixture, remove_html_footer, remove_html_link_tags


def test_build_example(testing_app):
	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')"):
		testing_app.build()
		testing_app.build()


@pytest.mark.parametrize("page", ["example.html"], indirect=True)
def test_example_html_output(page: BeautifulSoup, html_regression: HTMLRegressionFixture):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - reST Example" == title

	selector_string = "div.body div#sphinx-toolbox-demo-rest-example"

	body = list(filter(lambda a: a != '\n', page.select(selector_string)[0].contents))[1:]
	assert len(body) == 3

	assert body[0].name == 'p'
	assert body[0]["id"] == "example-0"
	assert body[0].contents == []

	assert body[1].name == "div"
	assert body[1]["class"] == ["rest-example", "docutils", "container"]

	body_body = list(filter(lambda a: a != '\n', body[1].contents))
	assert len(body_body) == 2

	assert body_body[0].name == "div"
	assert body_body[0]["class"] == ["highlight-rest", "notranslate"]

	assert body_body[0].contents[0].name == "div"
	assert body_body[0].contents[0]["class"] == ["highlight"]

	assert body_body[1].name == "div"
	assert body_body[1]["class"] == ["highlight-python", "notranslate"]

	assert body[2].name == 'p'
	assert body[2].contents == []


pages_to_check: List[Union[str, ParameterSet]] = [
		"assets.html",
		"augment-defaults.html",
		"autodoc-ellipsis.html",
		pytest.param(
				"autonamedtuple.html",
				marks=pytest.mark.skipif(
						condition=sys.version_info >= (3, 10),
						reason="Output differs on Python 3.10",
						),
				id="autonamedtuple.html"
				),
		pytest.param(
				"autonamedtuple.html",
				marks=min_version((3, 10), reason="Output differs on Python 3.10"),
				id="autonamedtuple_3_10",
				),
		"autoprotocol.html",
		"autotypeddict.html",
		"code-block.html",
		"changeset.html",
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
		"documentation-summary.html",
		"documentation-summary-meta.html",
		"github.html",
		"latex.html",
		"collapse.html",
		"footnote_symbols.html",
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
				"autonamedtuple_pep563.html",
				marks=min_version(3.7, reason="Output differs on Python 3.6, and not as relevant."),
				id="autonamedtuple_pep563"
				),
		pytest.param(
				"genericalias.html",
				marks=min_version(3.7, reason="Output differs on Python 3.6"),
				id="genericalias"
				),
		]


def test_html_output(testing_app, html_regression: HTMLRegressionFixture):
	"""
	Parametrize new files here rather than as their own function.
	"""

	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')"):
		testing_app.build(force_all=True)

	caught_exceptions: List[BaseException] = []

	for page in pages_to_check:
		if isinstance(page, str):
			page = pytest.param(page, id=page)

		pagename: str = page.values[0]  # type: ignore
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
			content = (testing_app.outdir / pagename).read_text()
			try:
				html_regression.check(BeautifulSoup(content, "html5lib"), extension=f"_{page_id}_.html")
			except BaseException as e:
				caught_exceptions.append(e)

		continue

	print(caught_exceptions)

	for exception in caught_exceptions:
		raise exception


def test_sidebar_links_output(testing_app, advanced_file_regression: AdvancedFileRegressionFixture):
	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')"):
		testing_app.build(force_all=True)

	content = (testing_app.outdir / "index.html").read_text()

	page = BeautifulSoup(content, "html5lib")
	page = remove_html_footer(page)
	page = remove_html_link_tags(page)

	for div in page.select("script"):
		if "_static/language_data.js" in str(div):
			div.extract()

	advanced_file_regression.check(
			str(StringList(page.prettify())),
			extension=".html",
			)


@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output(app, advanced_file_regression: AdvancedFileRegressionFixture):

	assert app.builder.name.lower() == "latex"

	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')"):
		app.build()

	output_file = PathPlus(app.outdir / "python.tex")
	content = StringList(output_file.read_lines())
	advanced_file_regression.check(
			re.sub(r"\\date{.*}", r"\\date{Mar 11, 2021}", str(content).replace("\\sphinxAtStartPar\n", '')),
			extension=".tex",
			)


@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output_latex_layout(app, advanced_file_regression: AdvancedFileRegressionFixture):

	assert app.builder.name.lower() == "latex"

	app.setup_extension("sphinx_toolbox.tweaks.latex_layout")
	app.events.emit("config-inited", app.config)

	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')") as w:
		app.build(force_all=True)

	output_file = PathPlus(app.outdir / "python.tex")
	content = StringList(output_file.read_lines())
	advanced_file_regression.check(
			re.sub(r"\\date{.*}", r"\\date{Mar 11, 2021}", str(content)),
			extension=".tex",
			)


@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output_better_header_layout(app, advanced_file_regression: AdvancedFileRegressionFixture):

	assert app.builder.name.lower() == "latex"

	better_header_layout(app.config, 9, 19)
	app.builder.context.update(app.config.latex_elements)

	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')") as w:
		app.build(force_all=True)

	output_file = PathPlus(app.outdir / "python.tex")
	content = StringList(output_file.read_lines())
	advanced_file_regression.check(
			re.sub(r"\\date{.*}", r"\\date{Mar 11, 2021}", str(content).replace("\\sphinxAtStartPar\n", '')),
			extension=".tex",
			)


@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output_autosummary_col_type(app, advanced_file_regression: AdvancedFileRegressionFixture):

	assert app.builder.name.lower() == "latex"
	app.config.autosummary_col_type = r"\Y"

	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')"):
		app.build()

	output_file = PathPlus(app.outdir / "python.tex")
	content = StringList(output_file.read_lines())
	advanced_file_regression.check(
			re.sub(r"\\date{.*}", r"\\date{Mar 11, 2021}", str(content).replace("\\sphinxAtStartPar\n", '')),
			extension=".tex",
			)

# stdlib
import sys
from pprint import pformat
from typing import List

# 3rd party
import docutils
import docutils.nodes
import pytest
import sphinx
import sphinx.writers.html5
from _pytest.mark import ParameterSet
from bs4 import BeautifulSoup  # type: ignore[import]
from coincidence.params import param
from coincidence.regressions import AdvancedFileRegressionFixture
from coincidence.selectors import min_version
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from jinja2 import Template
from pytest_regressions.common import check_text_files

# this package
from sphinx_toolbox.latex import better_header_layout
from sphinx_toolbox.testing import (
		HTMLRegressionFixture,
		LaTeXRegressionFixture,
		remove_html_footer,
		remove_html_link_tags
		)


def test_build_example(testing_app):
	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')"):
		testing_app.build()
		testing_app.build()


@pytest.mark.usefixtures("docutils_17_compat")
@pytest.mark.parametrize("page", ["example.html"], indirect=True)
def test_example_html_output(page: BeautifulSoup):
	# Make sure the page title is what you expect
	title = page.find("h1").contents[0].strip()
	assert "sphinx-toolbox Demo - reST Example" == title

	selector_string = "div.body div#sphinx-toolbox-demo-rest-example"

	body = list(filter(lambda a: a != '\n', page.select(selector_string)[0].contents))[1:]
	assert len(body) == 3, pformat(body)

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


pages_to_check: List[ParameterSet] = [
		param("assets.html", idx=0),
		param("augment-defaults.html", idx=0),
		param("autodoc-ellipsis.html", idx=0),
		pytest.param(
				"autonamedtuple.html",
				True,
				marks=pytest.mark.skipif(
						condition=sys.version_info >= (3, 10),
						reason="Output differs on Python 3.10",
						),
				id="autonamedtuple.html"
				),
		pytest.param(
				"autonamedtuple.html",
				True,
				marks=min_version((3, 10), reason="Output differs on Python 3.10"),
				id="autonamedtuple_3_10",
				),
		param("autoprotocol.html", idx=0),
		param("autotypeddict.html", idx=0),
		param("code-block.html", idx=0),
		param("changeset.html", idx=0),
		param("confval.html", idx=0),
		param("decorators.html", idx=0),
		param("example.html", idx=0),
		param("flake8.html", idx=0),
		param("formatting.html", idx=0),
		param("installation.html", idx=0),
		param("no_docstring.html", idx=0),
		param("overloads.html", idx=0),
		param("pre-commit.html", idx=0),
		param("regex.html", idx=0),
		param("shields.html", idx=0),
		param("sourcelink.html", idx=0),
		param("typevars.html", idx=0),
		param("variables.html", idx=0),
		param("wikipedia.html", idx=0),
		param("documentation-summary.html", idx=0),
		param("documentation-summary-meta.html", idx=0),
		param("github.html", idx=0),
		param("latex.html", idx=0),
		param("collapse.html", idx=0),
		param("footnote_symbols.html", idx=0),
		param("instancevar.html", idx=0),
		pytest.param(
				"generic_bases.html",
				marks=min_version(3.7, reason="Output differs on Python 3.8+"),
				id="generic_bases"
				),
		pytest.param("autonamedtuple_pep563.html", id="autonamedtuple_pep563"),
		pytest.param("genericalias.html", id="genericalias"),
		]


@pytest.mark.usefixtures("docutils_17_compat")
def test_html_output(testing_app, html_regression: HTMLRegressionFixture):
	"""
	Parametrize new files here rather than as their own function.
	"""

	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')"):
		testing_app.build(force_all=True)

	caught_exceptions: List[BaseException] = []

	for page in pages_to_check:
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
			content = (testing_app.outdir / pagename).read_text()
			try:
				html_regression.check(
						BeautifulSoup(content, "html5lib"),
						extension=f"_{page_id}_.html",
						jinja2=True,
						)
			except BaseException as e:
				caught_exceptions.append(e)

		continue

	print(caught_exceptions)

	for exception in caught_exceptions:
		raise exception


def test_sidebar_links_output(testing_app, advanced_file_regression: AdvancedFileRegressionFixture, monkeypatch):

	def visit_caption(self, node) -> None:
		if isinstance(node.parent, docutils.nodes.container) and node.parent.get("literal_block"):
			self.body.append('<div class="code-block-caption">')
		else:
			self.body.append(self.starttag(node, 'p', '', CLASS="caption"))
		self.add_fignumber(node.parent)
		self.body.append(self.starttag(node, "span", '', CLASS="caption-text"))

	def depart_caption(self, node):
		self.body.append('</p>\n')

	monkeypatch.setattr(sphinx.writers.html5.HTML5Translator, "visit_caption", visit_caption)
	monkeypatch.setattr(sphinx.writers.html5.HTML5Translator, "depart_caption", depart_caption)

	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')"):
		testing_app.build(force_all=True)

	content = (testing_app.outdir / "index.html").read_text()

	page = BeautifulSoup(content, "html5lib")
	page = remove_html_footer(page)
	page = remove_html_link_tags(page)

	for div in page.select("script"):
		if "_static/language_data.js" in str(div):
			div.extract()

	def check_fn(obtained_filename, expected_filename):
		print(obtained_filename, expected_filename)
		expected_filename = PathPlus(expected_filename)
		template = Template(expected_filename.read_text())

		expected_filename.write_text(
				template.render(
						sphinx_version=sphinx.version_info,
						python_version=sys.version_info,
						docutils_version=docutils.__version_info__,
						)
				)

		return check_text_files(obtained_filename, expected_filename, encoding="UTF-8")

	advanced_file_regression.check(
			str(StringList(page.prettify())),
			extension=".html",
			check_fn=check_fn,
			)


@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output(app, latex_regression: LaTeXRegressionFixture):

	assert app.builder.name.lower() == "latex"

	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')"):
		app.build()

	output_file = PathPlus(app.outdir / "python.tex")
	latex_regression.check(StringList(output_file.read_lines()), jinja2=True)


@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output_latex_layout(app, latex_regression: LaTeXRegressionFixture):

	assert app.builder.name.lower() == "latex"

	app.setup_extension("sphinx_toolbox.tweaks.latex_layout")
	app.config.needspace_amount = r"4\baselineskip"
	app.events.emit("config-inited", app.config)

	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')") as w:
		app.build(force_all=True)

	output_file = PathPlus(app.outdir / "python.tex")
	latex_regression.check(StringList(output_file.read_lines()), jinja2=True)


@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output_better_header_layout(app, latex_regression: LaTeXRegressionFixture):

	assert app.builder.name.lower() == "latex"

	better_header_layout(app.config, 9, 19)
	app.builder.context.update(app.config.latex_elements)

	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')"):
		app.build(force_all=True)

	output_file = PathPlus(app.outdir / "python.tex")
	latex_regression.check(StringList(output_file.read_lines()), jinja2=True)


@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output_autosummary_col_type(app, latex_regression: LaTeXRegressionFixture):

	assert app.builder.name.lower() == "latex"
	app.config.autosummary_col_type = r"\Y"

	with pytest.warns(UserWarning, match="(No codes specified|No such code 'F401')"):
		app.build()

	output_file = PathPlus(app.outdir / "python.tex")
	latex_regression.check(StringList(output_file.read_lines()), jinja2=True)

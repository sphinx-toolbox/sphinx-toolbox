# stdlib
import sys
from pathlib import Path
from pprint import pformat
from typing import Callable, ContextManager, Dict, List, Optional, cast

# 3rd party
import docutils
import docutils.nodes
import pytest
import sphinx
import sphinx.writers.html5
from _pytest.mark import ParameterSet
from bs4 import BeautifulSoup, PageElement, Tag
from coincidence.params import param
from coincidence.regressions import AdvancedFileRegressionFixture
from coincidence.selectors import min_version
from docutils import nodes
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.stringlist import StringList
from domdf_python_tools.typing import PathLike
from jinja2 import Template
from pytest_regressions.common import check_text_files
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.latex import better_header_layout
from sphinx_toolbox.testing import (
		HTMLRegressionFixture,
		LaTeXRegressionFixture,
		remove_html_footer,
		remove_html_link_tags
		)
from sphinx_toolbox.utils import Config


@pytest.mark.usefixtures("pre_commit_hooks")
def test_build_example(
		testing_app: Sphinx,
		pre_commit_flake8_contextmanager: Callable[[], ContextManager],
		):
	with pre_commit_flake8_contextmanager():
		testing_app.build()
		testing_app.build()


@pytest.mark.usefixtures("docutils_17_compat", "pre_commit_hooks")
@pytest.mark.parametrize("page", ["example.html"], indirect=True)
def test_example_html_output(page: BeautifulSoup):
	# Make sure the page title is what you expect
	h1 = cast(Optional[Tag], page.find("h1"))
	assert h1 is not None
	title = cast(str, h1.contents[0]).strip()
	assert "sphinx-toolbox Demo - reST Example" == title

	selector_string = "div.body div#sphinx-toolbox-demo-rest-example"

	body = list(filter(lambda a: a != '\n', page.select(selector_string)[0].contents))[1:]
	assert len(body) == 3, pformat(body)

	assert body[0].name == 'p'  # type: ignore[attr-defined]
	assert body[0]["id"] == "example-0"  # type: ignore[index]
	assert body[0].contents == []  # type: ignore[attr-defined]

	assert body[1].name == "div"  # type: ignore[attr-defined]
	assert body[1]["class"] == ["rest-example", "docutils", "container"]  # type: ignore[index]

	body_body: List[PageElement] = list(
			filter(lambda a: a != '\n', body[1].contents),  # type: ignore[arg-type,attr-defined]
			)
	assert len(body_body) == 2

	assert body_body[0].name == "div"  # type: ignore[attr-defined]
	assert body_body[0]["class"] == ["highlight-rest", "notranslate"]  # type: ignore[index]

	assert body_body[0].contents[0].name == "div"  # type: ignore[attr-defined]
	assert body_body[0].contents[0]["class"] == ["highlight"]  # type: ignore[attr-defined]

	assert body_body[1].name == "div"  # type: ignore[attr-defined]
	assert body_body[1]["class"] == ["highlight-python", "notranslate"]  # type: ignore[index]

	assert body[2].name == 'p'  # type: ignore[attr-defined]
	assert body[2].contents == []  # type: ignore[attr-defined]


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
				id="autonamedtuple.html",
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
				id="generic_bases",
				),
		pytest.param("autonamedtuple_pep563.html", id="autonamedtuple_pep563"),
		pytest.param(
				"genericalias.html",
				id="genericalias",
				marks=pytest.mark.skipif(
						condition=sys.version_info >= (3, 13),
						reason="Link not created on 3.13",
						),
				),  # Should be xfail
		]


@pytest.mark.usefixtures("docutils_17_compat", "pre_commit_hooks")
def test_html_output(
		testing_app: Sphinx,
		html_regression: HTMLRegressionFixture,
		pre_commit_flake8_contextmanager: Callable[[], ContextManager],
		):
	"""
	Parametrize new files here rather than as their own function.
	"""

	with pre_commit_flake8_contextmanager():
		testing_app.build(force_all=True)

	caught_exceptions: List[BaseException] = []

	for page in pages_to_check:
		pagename: str = page.values[0]  # type: ignore[assignment]
		page_id: str = cast(str, page.id or pagename)

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
			content = (PathPlus(testing_app.outdir) / pagename).read_text()

			soup = BeautifulSoup(content, "html5lib")

			for meta in cast(List[Dict], soup.find_all("meta")):
				if meta.get("content", '') == "width=device-width, initial-scale=0.9, maximum-scale=0.9":
					meta.extract()  # type: ignore[attr-defined]

			try:
				html_regression.check(soup, extension=f"_{page_id}_.html", jinja2=True)
			except BaseException as e:
				caught_exceptions.append(e)

		continue

	print(caught_exceptions)

	for exception in caught_exceptions:
		raise exception


@pytest.mark.skipif(sphinx.version_info >= (8, 1), reason="Currently failing on Sphinx 8.1")
@pytest.mark.usefixtures("pre_commit_hooks")
def test_sidebar_links_output(
		testing_app: Sphinx,
		advanced_file_regression: AdvancedFileRegressionFixture,
		monkeypatch,
		pre_commit_flake8_contextmanager: Callable[[], ContextManager],
		):

	def visit_caption(self, node: nodes.Node) -> None:
		if isinstance(node.parent, docutils.nodes.container) and node.parent.get("literal_block"):
			self.body.append('<div class="code-block-caption">')
		else:
			self.body.append(self.starttag(node, 'p', '', CLASS="caption"))
		self.add_fignumber(node.parent)
		self.body.append(self.starttag(node, "span", '', CLASS="caption-text"))

	def depart_caption(self, node: nodes.Node) -> None:
		self.body.append('</p>\n')

	monkeypatch.setattr(sphinx.writers.html5.HTML5Translator, "visit_caption", visit_caption)
	monkeypatch.setattr(sphinx.writers.html5.HTML5Translator, "depart_caption", depart_caption)

	with pre_commit_flake8_contextmanager():
		testing_app.build(force_all=True)

	content = (PathPlus(testing_app.outdir) / "index.html").read_text()

	page = BeautifulSoup(content, "html5lib")

	for meta in cast(List[Dict], page.find_all("meta")):
		if meta.get("content", '') == "width=device-width, initial-scale=0.9, maximum-scale=0.9":
			meta.extract()  # type: ignore[attr-defined]

	page = remove_html_footer(page)
	page = remove_html_link_tags(page)

	for div in page.select("div.related"):
		if div["aria-label"] == "Related":
			div.extract()

	for div in page.select("script"):
		if "_static/language_data.js" in str(div):
			div.extract()

	def check_fn(obtained_filename: Path, expected_filename: PathLike):  # noqa: MAN002
		print(obtained_filename, expected_filename)
		expected_filename = PathPlus(expected_filename)
		template = Template(expected_filename.read_text())

		expected_filename.write_text(
				template.render(
						sphinx_version=sphinx.version_info,
						python_version=sys.version_info,
						docutils_version=docutils.__version_info__,
						),
				)

		return check_text_files(obtained_filename, expected_filename, encoding="UTF-8")

	advanced_file_regression.check(
			str(StringList(page.prettify())),
			extension=".html",
			check_fn=check_fn,
			)


@pytest.mark.usefixtures("pre_commit_hooks")
@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output(
		app: Sphinx,
		latex_regression: LaTeXRegressionFixture,
		pre_commit_flake8_contextmanager: Callable[[], ContextManager],
		):

	assert app.builder is not None
	assert app.builder.name.lower() == "latex"

	with pre_commit_flake8_contextmanager():
		app.build()

	output_file = PathPlus(app.outdir) / "python.tex"
	latex_regression.check(StringList(output_file.read_lines()), jinja2=True)


@pytest.mark.usefixtures("pre_commit_hooks")
@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output_latex_layout(
		app: Sphinx,
		latex_regression: LaTeXRegressionFixture,
		pre_commit_flake8_contextmanager: Callable[[], ContextManager],
		):

	assert app.builder is not None
	assert app.builder.name.lower() == "latex"

	app.setup_extension("sphinx_toolbox.tweaks.latex_layout")
	app.config.needspace_amount = r"4\baselineskip"  # type: ignore[attr-defined]
	app.config.intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}  # type: ignore[attr-defined]
	app.events.emit("config-inited", app.config)

	with pre_commit_flake8_contextmanager():
		app.build(force_all=True)

	output_file = PathPlus(app.outdir) / "python.tex"
	latex_regression.check(StringList(output_file.read_lines()), jinja2=True)


@pytest.mark.usefixtures("pre_commit_hooks")
@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output_better_header_layout(
		app: Sphinx,
		latex_regression: LaTeXRegressionFixture,
		pre_commit_flake8_contextmanager: Callable[[], ContextManager],
		):

	assert app.builder is not None
	assert app.builder.name.lower() == "latex"

	better_header_layout(cast(Config, app.config), 9, 19)
	app.builder.context.update(app.config.latex_elements)  # type: ignore[attr-defined]

	with pre_commit_flake8_contextmanager():
		app.build(force_all=True)

	output_file = PathPlus(app.outdir) / "python.tex"
	latex_regression.check(StringList(output_file.read_lines()), jinja2=True)


@pytest.mark.usefixtures("pre_commit_hooks")
@pytest.mark.sphinx("latex", srcdir="test-root")
def test_latex_output_autosummary_col_type(
		app: Sphinx,
		latex_regression: LaTeXRegressionFixture,
		pre_commit_flake8_contextmanager: Callable[[], ContextManager],
		):

	assert app.builder is not None
	assert app.builder.name.lower() == "latex"
	app.config.autosummary_col_type = r"\Y"  # type: ignore[attr-defined]

	with pre_commit_flake8_contextmanager():
		app.build()

	output_file = PathPlus(app.outdir) / "python.tex"
	latex_regression.check(StringList(output_file.read_lines()), jinja2=True)

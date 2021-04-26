# stdlib
import re

# 3rd party
import pytest
from coincidence.regressions import AdvancedFileRegressionFixture
from sphinx.events import EventListener
from sphinx.ext.autodoc.directive import AutodocDirective

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc import regex
from sphinx_toolbox.testing import check_asset_copy, run_setup
from tests.regex_demo import no_flags, one_flag, two_flags

parser = regex.RegexParser()


@pytest.mark.parametrize(
		"regex, expected",
		[
				(
						re.compile(r"(?s)(\.\. start installation)(.*?)(\.\. end installation)"),
						"(.. start installation)(.*?)(.. end installation)",
						),
				(
						re.compile(r"[A-Za-z_]\w*"),
						r"[A-Za-z_]\w*",
						),
				(
						re.compile(r"^:(param|parameter|arg|argument)\s*"),
						r"^:(param|parameter|arg|argument)\s*",
						),
				(
						re.compile("^:(default|Default)[ ]"),
						"^:(default|Default)[ ]",
						),
				(
						re.compile("^:(default|Default) "),
						"^:(default|Default)[ ]",
						),
				(
						re.compile(r"\A:(default|Default) "),
						r"\A:(default|Default)[ ]",
						),
				(
						re.compile("^:(default|Default)   "),
						"^:(default|Default) {3}",
						),
				(
						re.compile(":(default|Default)   $"),
						":(default|Default)   $",
						),
				(
						re.compile(r":(default|Default)   \Z"),
						r":(default|Default)   \Z",
						),
				(
						re.compile(" :(default|Default)"),
						"[ ]:(default|Default)",
						),
				(
						re.compile("   :(default|Default)"),
						"[ ]{3}:(default|Default)",
						),
				(
						re.compile("[ ]:(default|Default)"),
						"[ ]:(default|Default)",
						),
				(
						re.compile("hello (world)?"),
						"hello (world)?",
						),
				(
						re.compile("(hello){1,3} (world)?"),
						"(hello){1,3} (world)?",
						),
				(
						re.compile("(hello){3,3} (world)?"),
						"(hello){3} (world)?",
						),
				(
						re.compile(r"Issue #\d"),
						"Issue #\\d",
						),
				(
						re.compile(r"Hello \w"),
						"Hello \\w",
						),
				(
						re.compile(r"Not a word: \W"),
						"Not a word: \\W",
						),
				(
						re.compile(r"Not whitespace: \S"),
						"Not whitespace: \\S",
						),
				(
						re.compile(r"Not a number: \D"),
						"Not a number: \\D",
						),
				(no_flags, no_flags.pattern.replace("\\?", '?')),
				(one_flag, one_flag.pattern.replace("\\?", '?')),
				(two_flags, "Hello\\s+[Ww]orld[.,](Lovely|Horrible) weather, isn't it(.*)?"),
				]
		)
def test_regex_parser(regex, expected):
	assert parser.parse_pattern(regex) == expected


def test_copy_asset_files(tmp_pathplus, advanced_file_regression: AdvancedFileRegressionFixture):
	check_asset_copy(
			regex.copy_asset_files,
			"_static/regex.css",
			file_regression=advanced_file_regression,
			)


@pytest.mark.parametrize(
		"flags, expected",
		[
				pytest.param(re.ASCII, ":py:data:`re.ASCII`", id="re.ASCII"),
				pytest.param(re.DEBUG, ":py:data:`re.DEBUG`", id="re.DEBUG"),
				pytest.param(re.IGNORECASE, ":py:data:`re.IGNORECASE`", id="re.IGNORECASE"),
				pytest.param(re.LOCALE, ":py:data:`re.LOCALE`", id="re.LOCALE"),
				pytest.param(re.MULTILINE, ":py:data:`re.MULTILINE`", id="re.MULTILINE"),
				pytest.param(re.DOTALL, ":py:data:`re.DOTALL`", id="re.DOTALL"),
				pytest.param(re.VERBOSE, ":py:data:`re.VERBOSE`", id="re.VERBOSE"),
				pytest.param(
						re.VERBOSE | re.IGNORECASE,
						":py:data:`re.IGNORECASE` ``|`` :py:data:`re.VERBOSE`",
						id="re.VERBOSE|re.IGNORECASE"
						),
				]
		)
def test_parse_regex_flags(flags: int, expected: str):
	assert regex.parse_regex_flags(flags) == expected


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(regex.setup)

	assert setup_ret == {"parallel_read_safe": True, "version": __version__}

	assert directives == {"autoregex": AutodocDirective}
	assert "regex" in roles
	assert isinstance(roles["regex"], regex.Regex)
	assert additional_nodes == {regex.RegexNode}

	assert app.registry.documenters["regex"] == regex.RegexDocumenter

	assert app.events.listeners == {
			"build-finished": [EventListener(id=0, handler=regex.copy_asset_files, priority=500)],
			}

	assert app.registry.css_files == [("regex.css", {})]

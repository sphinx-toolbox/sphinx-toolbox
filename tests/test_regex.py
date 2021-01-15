# stdlib
import re

# 3rd party
import pytest
from pytest_regressions.file_regression import FileRegressionFixture

# this package
from sphinx_toolbox.more_autodoc.regex import RegexParser, copy_asset_files
from sphinx_toolbox.testing import check_asset_copy
from tests.regex_demo import no_flags, one_flag, two_flags

parser = RegexParser()


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
						re.compile("^:(default|Default)   "),
						"^:(default|Default) {3}",
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
				(no_flags, no_flags.pattern.replace("\\?", '?')),
				(one_flag, one_flag.pattern.replace("\\?", '?')),
				(two_flags, two_flags.pattern.replace("\\?", '?')),
				]
		)
def test_regex_parser(regex, expected):
	assert parser.parse_pattern(regex) == expected


def test_copy_asset_files(tmp_pathplus, file_regression: FileRegressionFixture):
	check_asset_copy(
			copy_asset_files,
			"_static/regex.css",
			file_regression=file_regression,
			)

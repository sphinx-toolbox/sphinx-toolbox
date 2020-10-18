# stdlib
import re

# 3rd party
import pytest

# this package
from sphinx_toolbox.more_autodoc.regex import RegexParser
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
				(no_flags, no_flags.pattern.replace("\\?", '?')),
				(one_flag, one_flag.pattern.replace("\\?", '?')),
				(two_flags, two_flags.pattern.replace("\\?", '?')),
				]
		)
def test_regex_parser(regex, expected):
	assert parser.parse_pattern(regex) == expected

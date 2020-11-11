# stdlib
import string

# 3rd party
import pytest
from apeye.url import RequestsURL
from domdf_python_tools.utils import strtobool
from hypothesis import given
from hypothesis.strategies import text

# this package
from sphinx_toolbox.utils import (
		NoMatchError,
		escape_trailing__,
		flag,
		get_first_matching,
		make_github_url,
		singleton
		)


def test_make_github_url():
	url = make_github_url("domdfcoding", "sphinx-toolbox")
	assert isinstance(url, RequestsURL)

	assert url == RequestsURL("https://github.com/domdfcoding/sphinx-toolbox")


def test_flag():
	assert flag('')
	assert flag(' ')
	assert flag("  ")
	assert flag("   ")
	assert flag("    ")
	assert flag('\t')

	assert flag(False)

	with pytest.raises(AttributeError):
		flag(True)

	with pytest.raises(ValueError, match="No argument is allowed; 'hello' supplied"):
		flag("hello")


def test_get_first_matching():

	assert get_first_matching(strtobool, [True, "True", 0, "False", False])
	assert get_first_matching(strtobool, (True, "True", 0, "False", False))

	with pytest.raises(
			NoMatchError,
			match=r"No matching values for '<function strtobool at .*>' in \[0, 'False', False\]",
			):
		get_first_matching(strtobool, [0, "False", False])

	assert get_first_matching(strtobool, [0, "False", False], default=True)

	assert get_first_matching(lambda x: x.isupper(), string.ascii_letters) == 'A'

	with pytest.raises(
			ValueError,
			match="The condition must evaluate to True for the default value.",
			):
		get_first_matching(lambda x: x.isdigit(), string.ascii_letters, default='A')


def test_singleton():

	s = singleton('s')

	assert str(s) == 's'
	assert repr(s) == 's'

	assert s is s
	assert s is s.__class__()
	assert s is type(s)()


@given(text(alphabet=string.ascii_letters + string.digits, min_size=1))
def test_escape_trailing_underscore(s):

	assert escape_trailing__(s) == s

	assert escape_trailing__(f"{s}_") == rf"{s}\_"
	assert escape_trailing__(f"{s}__") == rf"{s}_\_"
	assert escape_trailing__(f"_{s}") == f"_{s}"

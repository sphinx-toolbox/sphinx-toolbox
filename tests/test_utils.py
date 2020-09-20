# 3rd party
import pytest
from apeye.url import RequestsURL

# this package
from sphinx_toolbox.utils import flag, make_github_url


def test_make_github_url():
	url = make_github_url("domdfcoding", "sphinx-toolbox")
	assert isinstance(url, RequestsURL)

	assert url == RequestsURL("https://github.com/domdfcoding/sphinx-toolbox")


def test_flag():
	assert flag('')
	assert flag(" ")
	assert flag("  ")
	assert flag("   ")
	assert flag("    ")
	assert flag("\t")

	assert flag(False)

	with pytest.raises(AttributeError):
		flag(True)

	with pytest.raises(ValueError, match="No argument is allowed; 'hello' supplied"):
		flag("hello")

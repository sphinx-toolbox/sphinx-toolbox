# 3rd party
from apeye.url import RequestsURL

# this package
from sphinx_toolbox.utils import make_github_url


def test_make_github_url():
	assert isinstance(make_github_url("domdfcoding", "sphinx-toolbox"), RequestsURL)
	assert make_github_url("domdfcoding",
							"sphinx-toolbox") == RequestsURL("https://github.com/domdfcoding/sphinx-toolbox")

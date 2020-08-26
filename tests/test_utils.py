# 3rd party
from apeye.url import RequestsURL

# this package
from sphinx_toolbox.utils import make_github_url


def test_make_github_url():
	url = make_github_url("domdfcoding", "sphinx-toolbox")
	assert isinstance(url, RequestsURL)

	assert url == RequestsURL("https://github.com/domdfcoding/sphinx-toolbox")

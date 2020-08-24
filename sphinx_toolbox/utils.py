# stdlib
import functools

# 3rd party
from apeye.url import RequestsURL

__all__ = ["make_github_url"]

GITHUB_COM = RequestsURL("https://github.com")


@functools.lru_cache()
def make_github_url(username: str, repository: str) -> RequestsURL:
	return GITHUB_COM / username / repository

# 3rd party
import pytest
from apeye.url import RequestsURL

# this package
from sphinx_toolbox.utils import flag, make_github_url, word_join


def test_make_github_url():
	url = make_github_url("domdfcoding", "sphinx-toolbox")
	assert isinstance(url, RequestsURL)

	assert url == RequestsURL("https://github.com/domdfcoding/sphinx-toolbox")


def test_word_join():
	assert word_join([]) == ''

	assert word_join(["bob"]) == "bob"
	assert word_join(["bob", "alice"]) == "bob and alice"
	assert word_join(["bob", "alice", "fred"]) == "bob, alice and fred"

	assert word_join(["bob"], use_repr=True) == "'bob'"
	assert word_join(["bob", "alice"], use_repr=True) == "'bob' and 'alice'"
	assert word_join(["bob", "alice", "fred"], use_repr=True) == "'bob', 'alice' and 'fred'"

	assert word_join(["bob"], use_repr=True, oxford=True) == "'bob'"
	assert word_join(["bob", "alice"], use_repr=True, oxford=True) == "'bob' and 'alice'"
	assert word_join(["bob", "alice", "fred"], use_repr=True, oxford=True) == "'bob', 'alice', and 'fred'"

	assert word_join(()) == ''

	assert word_join(("bob", )) == "bob"
	assert word_join(("bob", "alice")) == "bob and alice"
	assert word_join(("bob", "alice", "fred")) == "bob, alice and fred"

	assert word_join(("bob", ), use_repr=True) == "'bob'"
	assert word_join(("bob", "alice"), use_repr=True) == "'bob' and 'alice'"
	assert word_join(("bob", "alice", "fred"), use_repr=True) == "'bob', 'alice' and 'fred'"

	assert word_join(("bob", ), use_repr=True, oxford=True) == "'bob'"
	assert word_join(("bob", "alice"), use_repr=True, oxford=True) == "'bob' and 'alice'"
	assert word_join(("bob", "alice", "fred"), use_repr=True, oxford=True) == "'bob', 'alice', and 'fred'"


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

# 3rd party
from docutils import nodes

# this package
from sphinx_toolbox import wikipedia
from sphinx_toolbox.testing import run_setup


def test_make_wikipedia_link(monkeypatch):
	monkeypatch.setattr(wikipedia, "_get_wikipedia_lang", lambda *args: "en")

	generated_nodes, warnings = wikipedia.make_wikipedia_link(
		"wikipedia",
		":wikipedia:`Python (programming language)`",
		"Python (programming language)",
		lineno=27,
		inliner=None,  # type: ignore[arg-type]
		)

	assert isinstance(generated_nodes, list)
	assert generated_nodes
	assert isinstance(generated_nodes[0], nodes.reference)
	assert generated_nodes[0].rawsource == ":wikipedia:`Python (programming language)`"
	assert generated_nodes[0].astext() == "Python (programming language)"
	assert generated_nodes[0]["refuri"] == "https://en.wikipedia.org/wiki/Python_%28programming_language%29"

	assert isinstance(warnings, list)
	assert not warnings


def test_make_wikipedia_link_lang(monkeypatch):
	generated_nodes, warnings = wikipedia.make_wikipedia_link(
		"wikipedia",
		":wikipedia:`:zh:斯芬克斯`",
		":zh:斯芬克斯",
		lineno=27,
		inliner=None,  # type: ignore[arg-type]
		)

	assert isinstance(generated_nodes, list)
	assert generated_nodes
	assert isinstance(generated_nodes[0], nodes.reference)
	assert generated_nodes[0].rawsource == ":wikipedia:`:zh:斯芬克斯`"
	assert generated_nodes[0].astext() == "斯芬克斯"
	assert generated_nodes[0]["refuri"] == "https://zh.wikipedia.org/wiki/%E6%96%AF%E8%8A%AC%E5%85%8B%E6%96%AF"

	assert isinstance(warnings, list)
	assert not warnings


def test_make_wikipedia_link_with_label(monkeypatch):
	monkeypatch.setattr(wikipedia, "_get_wikipedia_lang", lambda *args: "en")

	generated_nodes, warnings = wikipedia.make_wikipedia_link(
		"wikipedia",
		":wikipedia:`Python <Python (programming language)>`",
		"Python <Python (programming language)>",
		lineno=27,
		inliner=None,  # type: ignore[arg-type]
		)

	assert isinstance(generated_nodes, list)
	assert generated_nodes
	assert isinstance(generated_nodes[0], nodes.reference)
	assert generated_nodes[0].rawsource == ":wikipedia:`Python <Python (programming language)>`"
	assert generated_nodes[0].astext() == "Python"
	assert generated_nodes[0]["refuri"] == "https://en.wikipedia.org/wiki/Python_%28programming_language%29"

	assert isinstance(warnings, list)
	assert not warnings


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(wikipedia.setup)

	assert roles == {"wikipedia": wikipedia.make_wikipedia_link}
	assert app.config.values["wikipedia_lang"] == ("en", "env", [str])
	assert app.registry.source_parsers == {}

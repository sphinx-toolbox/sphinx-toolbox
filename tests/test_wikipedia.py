# this package
from sphinx_toolbox import wikipedia
from sphinx_toolbox.testing import run_setup


def test_setup():
	setup_ret, directives, roles, additional_nodes, app = run_setup(wikipedia.setup)

	assert roles == {"wikipedia": wikipedia.make_wikipedia_link}
	assert app.config.values["wikipedia_lang"] == ("en", "env", [str])
	assert app.registry.source_parsers == {}

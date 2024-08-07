# 3rd party
from sphinx.application import Sphinx

# this package
from sphinx_toolbox import latex

extensions = [
		"sphinx.ext.viewcode",
		"sphinx_toolbox.more_autosummary",
		"sphinx_toolbox.more_autosummary.column_widths",
		]

github_username = "domdfcoding"
github_repository = "sphinx-toolbox"
source_link_target = "GitHub"

_exclude_members = "__repr__,__weakref__,__dict__,__annotations__,__firstlineno__,__replace__,__static_attributes__"
autodoc_default_options = {"exclude-members": _exclude_members}

all_typevars = True
no_unbound_typevars = False
sphinx_tabs_disable_tab_closing = True
html_codeblock_linenos_style = "table"

overloads_location = "bottom"
documentation_summary = "   This is an awesome tool! 🚀 ~ intersphinx_mapping #  100% 'Quotes'"

intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}
project = "Python"
author = "unknown"


def setup(app: Sphinx) -> None:
	app.connect("build-finished", latex.replace_unknown_unicode)

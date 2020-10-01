extensions = [
		"sphinx.ext.viewcode",
		"sphinx_toolbox",
		"sphinx_toolbox.more_autodoc.augment_defaults",
		"sphinx_toolbox.more_autodoc.typehints",
		"sphinx_toolbox.more_autodoc.genericalias",
		"sphinx_toolbox.more_autodoc.variables",
		"sphinx_toolbox.more_autodoc.no_docstring",
		"sphinx_toolbox.more_autodoc.sourcelink",
		"sphinx_toolbox.more_autodoc.regex",
		"sphinx_toolbox.more_autodoc.typevars",
		"sphinx_toolbox.more_autodoc.overloads",
		"sphinx_toolbox.more_autodoc.generic_bases",
		"sphinx_tabs.tabs",
		"sphinx-prompt",
		"sphinx.ext.autodoc",
		]

github_username = "domdfcoding"
github_repository = "sphinx-toolbox"
source_link_target = "GitHub"

autodoc_default_options = {
		"exclude-members": "__repr__",
		}

all_typevars = True
no_unbound_typevars = False

overloads_location = "bottom"

extensions = [
		"sphinx.ext.viewcode",
		"sphinx_toolbox",
		"sphinx_toolbox.more_autodoc.augment_defaults",
		"sphinx_toolbox.more_autodoc.typehints",
		"sphinx_toolbox.more_autodoc.genericalias",
		"sphinx_toolbox.more_autodoc.variables",
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

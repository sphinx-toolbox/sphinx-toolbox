extensions = [
		"sphinx.ext.viewcode",
		"sphinx_toolbox",
		"sphinx_toolbox.autodoc_augment_defaults",
		"sphinx_toolbox.autodoc_typehints",
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

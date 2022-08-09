# 3rd party
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import _

# this package
from sphinx_toolbox import latex

extensions = [
		"sphinx.ext.viewcode",
		"sphinx.ext.intersphinx",
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
		"sphinx_toolbox.documentation_summary",
		"sphinx_toolbox.tweaks.latex_toc",
		"sphinx_toolbox.tweaks.footnote_symbols",
		"sphinx_toolbox.flake8",
		"sphinx_toolbox.pre_commit",
		"sphinx_tabs.tabs",
		"sphinx-prompt",
		"sphinx.ext.autodoc",
		"sphinx_toolbox.more_autosummary",
		"sphinx_toolbox.latex.succinct_seealso",
		"sphinx_toolbox.tweaks.revert_footnote_style",
		]

github_username = "domdfcoding"
github_repository = "sphinx-toolbox"
source_link_target = "GitHub"

autodoc_default_options = {
		"exclude-members": "__repr__,__weakref__,__dict__,__annotations__",
		}

all_typevars = True
no_unbound_typevars = False
sphinx_tabs_disable_tab_closing = True
html_codeblock_linenos_style = "table"

overloads_location = "bottom"
documentation_summary = "   This is an awesome tool! 🚀 ~ intersphinx_mapping #  100% 'Quotes'"

intersphinx_mapping = {"python": ("https://docs.python.org/3/", None)}

rst_prolog = ".. |hello| replace:: world"


# These revert https://github.com/sphinx-doc/sphinx/pull/8472
def visit_desc_signature(self, node: addnodes.desc_signature) -> None:
	# the id is set automatically
	self.body.append(self.starttag(node, "dt"))


def depart_desc_signature(self, node: addnodes.desc_signature) -> None:
	if not node.get("is_multiline"):
		self.add_permalink_ref(node, _("Permalink to this definition"))
	self.body.append('</dt>\n')


def setup(app: Sphinx) -> None:
	app.connect("build-finished", latex.replace_unknown_unicode)
	app.add_node(addnodes.desc_signature, html=(visit_desc_signature, depart_desc_signature), override=True)


# TODO: add test matrix with this option enabled
# autodoc_typehints = "both"

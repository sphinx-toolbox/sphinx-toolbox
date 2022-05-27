# 3rd party
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.locale import _

extensions = [
		"sphinx.ext.viewcode",
		"sphinx.ext.autodoc",
		"sphinx_toolbox",
		"sphinx_toolbox.more_autodoc.generic_bases",
		"sphinx_toolbox.more_autodoc.autoprotocol",
		]

github_username = "domdfcoding"
github_repository = "sphinx-toolbox"
source_link_target = "GitHub"
generic_bases_fully_qualified = True


# These revert https://github.com/sphinx-doc/sphinx/pull/8472
def visit_desc_signature(self, node: addnodes.desc_signature) -> None:
	# the id is set automatically
	self.body.append(self.starttag(node, "dt"))


def depart_desc_signature(self, node: addnodes.desc_signature) -> None:
	if not node.get("is_multiline"):
		self.add_permalink_ref(node, _("Permalink to this definition"))
	self.body.append('</dt>\n')


def setup(app: Sphinx) -> None:
	app.add_node(addnodes.desc_signature, html=(visit_desc_signature, depart_desc_signature), override=True)

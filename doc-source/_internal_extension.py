# stdlib
from typing import Optional

# 3rd party
from domdf_python_tools import stringlist
from domdf_python_tools.paths import PathPlus
from sphinx import addnodes  # nodep
from sphinx.application import Sphinx  # nodep
from sphinx.config import Config
from sphinx.locale import admonitionlabels  # nodep
from sphinx.writers.latex import LaTeXTranslator  # nodep

# this package
from sphinx_toolbox import latex


def visit_seealso(translator: LaTeXTranslator, node: addnodes.seealso) -> None:
	"""
	Visit an :class:`addnodes.seealso`` node.

	:param translator:
	:param node:
	"""

	# 	translator.body.append('\n\n\\begin{description}\\item[{%s:}] \\leavevmode' % admonitionlabels['seealso'])
	translator.body.append('\n\n\\sphinxstrong{%s:} ' % admonitionlabels["seealso"])


def depart_seealso(translator: LaTeXTranslator, node: addnodes.seealso) -> None:
	"""
	Depart an :class:`addnodes.seealso`` node.

	:param translator:
	:param node:
	"""

	# translator.body.append("\\end{description}\n\n")
	translator.body.append("\n\n")


def replace_emoji(app: Sphinx, exception: Optional[Exception] = None):
	if exception:
		return

	if app.builder.name.lower() != "latex":
		return

	output_file = PathPlus(app.builder.outdir) / f"{app.builder.titles[0][1]}.tex"

	output_content = output_file.read_text()

	output_content = output_content.replace('🧰', '')
	output_content = output_content.replace('📔', '')
	output_content = output_content.replace(
			r"\sphinxcode{\sphinxupquote{\textbackslash{}vspace\{\}}}",
			r"\mbox{\sphinxcode{\sphinxupquote{\textbackslash{}vspace\{\}}}}",
			)

	output_file.write_clean(output_content)


def visit_desc(translator: LaTeXTranslator, node: addnodes.desc) -> None:
	"""
	Visit an :class:`addnodes.desc` node and add a custom table of contents label for the item, if required.

	:param translator:
	:param node:
	"""

	if node["domain"] == "py":
		translator.body.append(r"\needspace{5\baselineskip}")

	if "sphinxcontrib.toctree_plus" in translator.config.extensions:
		# 3rd party
		from sphinxcontrib import toctree_plus  # nodep

		toctree_plus.visit_desc(translator, node)
	else:
		LaTeXTranslator.visit_desc(translator, node)


def configure(app: Sphinx, config: Config):
	"""
	Configure Sphinx Extension.

	:param app: The Sphinx application.
	:param config:
	"""

	latex_elements = getattr(config, "latex_elements", {})

	latex_extrapackages = stringlist.StringList(latex_elements.get("extrapackages", ''))
	latex_extrapackages.append(r"\usepackage{needspace}")
	latex_elements["extrapackages"] = str(latex_extrapackages)

	config.latex_elements = latex_elements  # type: ignore


def setup(app: Sphinx):
	app.connect("config-inited", configure)
	app.connect("build-finished", replace_emoji)
	app.connect("build-finished", latex.replace_unknown_unicode)

	app.add_node(addnodes.seealso, latex=(visit_seealso, depart_seealso), override=True)
	app.add_node(addnodes.desc, latex=(visit_desc, LaTeXTranslator.depart_desc), override=True)

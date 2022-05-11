# stdlib
from typing import Optional

# 3rd party
from domdf_python_tools.paths import PathPlus
from sphinx.application import Sphinx  # nodep

# this package
from sphinx_toolbox import latex


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


def setup(app: Sphinx):
	app.connect("build-finished", replace_emoji)
	app.connect("build-finished", latex.replace_unknown_unicode)

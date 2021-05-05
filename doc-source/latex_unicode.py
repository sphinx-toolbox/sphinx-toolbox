# stdlib
from typing import Optional

# 3rd party
from domdf_python_tools.paths import PathPlus
from sphinx.application import Sphinx


def replace_unknown_unicode(app: Sphinx, exception: Optional[Exception] = None):
	if exception:
		return

	if app.builder.name.lower() != "latex":
		return

	output_file = PathPlus(app.builder.outdir) / f"{app.builder.titles[0][1]}.tex"

	output_content = output_file.read_text()

	output_content = output_content.replace('🧰', '')
	output_content = output_content.replace('📔', '')
	output_content = output_content.replace('♠', r' $\spadesuit$ ')
	output_content = output_content.replace('♥', r' $\heartsuit$ ')
	output_content = output_content.replace('♦', r' $\diamondsuit$ ')
	output_content = output_content.replace('♣', r' $\clubsuit$ ')

	output_file.write_clean(output_content)


def setup(app: Sphinx):
	app.connect("build-finished", replace_unknown_unicode)

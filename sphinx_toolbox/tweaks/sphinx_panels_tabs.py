#!/usr/bin/env python3
#
#  sphinx_panels_tabs.py
"""
Tweak to :github:repo:`executablebooks/sphinx-tabs`
to fix a CSS conflict with :github:repo:`executablebooks/sphinx-panels`.

Fix for :github:issue:`51 <executablebooks/sphinx-panels>`.

.. versionadded:: 1.9.0
.. extensions:: sphinx_toolbox.tweaks.sphinx_panels_tabs

-----

"""  # noqa: D400
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Parts based on https://github.com/executablebooks/sphinx-panels
#  Copyright (c) 2020 Executable Books
#  MIT Licensed
#

# stdlib
from typing import Optional

# 3rd party
import dict2css
from deprecation_alias import deprecated
from docutils import nodes
from domdf_python_tools.paths import PathPlus
from sphinx.application import Sphinx
from sphinx.writers.html import HTMLTranslator

# this package
from sphinx_toolbox import __version__, _css
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["copy_asset_files", "setup"]


def visit_container(self: HTMLTranslator, node: nodes.container):
	classes = "docutils container"
	if node.get("is_div", False):
		# we don't want the CSS for container for these nodes
		classes = "docutils"

	if any(c.startswith("sphinx-data-tab-") for c in node["classes"]):
		classes = "docutils"

	self.body.append(self.starttag(node, "div", CLASS=classes))


def depart_container(self: HTMLTranslator, node: nodes.Node):
	self.body.append("</div>\n")


def copy_asset_files(app: Sphinx, exception: Optional[Exception] = None) -> None:
	"""
	Copy asset files to the output.

	:param app: The Sphinx application.
	:param exception: Any exception which occurred and caused Sphinx to abort.

	.. versionchanged:: 2.7.0

		Renamed from ``copy_assets``.
		The old name is deprecated an will be removed in 3.0.0
	"""

	if exception:  # pragma: no cover
		return

	if app.builder is None or app.builder.format.lower() != "html":  # pragma: no cover
		return

	# style = StringList([
	# 		".docutils.container {",
	# 		"    padding-left: 0 !important;",
	# 		"    padding-right: 0 !important;",
	# 		'}',
	# 		'',
	# 		# "div.sphinx-tabs.docutils.container {",
	# 		# "    padding-left: 0 !important;",
	# 		# "    padding-right: 0 !important;",
	# 		# "}",
	# 		# '',
	# 		"div.ui.top.attached.tabular.menu.sphinx-menu.docutils.container {",
	# 		# "    padding-left: 0 !important;",
	# 		# "    padding-right: 0 !important;",
	# 		"    margin-left: 0 !important;",
	# 		"    margin-right: 0 !important;",
	# 		'}',
	# 		])

	css_static_dir = PathPlus(app.builder.outdir) / "_static" / "css"
	css_static_dir.maybe_make(parents=True)
	dict2css.dump(_css.tweaks_sphinx_panels_tabs_styles, css_static_dir / "tabs_customise.css")


copy_assets = deprecated(
		deprecated_in="2.7.0",
		removed_in="3.0.0",
		current_version=__version__,
		details="Renamed to 'copy_asset_files'",
		name="copy_assets",
		func=copy_asset_files,
		)


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.tweaks.sphinx_panels_tabs`.

	:param app: The Sphinx application.
	"""

	app.setup_extension("sphinx_tabs.tabs")
	app.setup_extension("sphinx_toolbox._css")

	app.add_node(nodes.container, override=True, html=(visit_container, depart_container))

	return {"parallel_read_safe": True}

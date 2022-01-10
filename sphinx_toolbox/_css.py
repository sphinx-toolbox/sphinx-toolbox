#!/usr/bin/env python3
#
#  _css.py
"""
Internal Sphinx extension to provide custom CSS.

.. versionadded:: 2.7.0
"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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

# stdlib
from typing import MutableMapping, Optional

# 3rd party
import dict2css
from domdf_python_tools.paths import PathPlus
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["copy_asset_files", "setup"]

installation_styles: MutableMapping[str, dict2css.Style] = {
		'div[id*="installation"] .sphinx-tabs-tab': {"color": "#2980b9"},
		"button.sphinx-tabs-tab,div.sphinx-tabs-panel": {"outline": (None, dict2css.IMPORTANT)},
		}

shields_styles: MutableMapping[str, dict2css.Style] = {
		".table-wrapper td p img.sphinx_toolbox_shield": {"vertical-align": "middle"},
		}

regex_styles: MutableMapping[str, dict2css.Style] = {
		"span.regex_literal": {"color": "dimgrey"},
		"span.regex_at": {"color": "orangered"},
		"span.regex_repeat_brace": {"color": "orangered"},
		"span.regex_branch": {"color": "orangered"},
		"span.regex_subpattern": {"color": "dodgerblue"},
		"span.regex_in": {"color": "darkorange"},
		"span.regex_category": {"color": "darkseagreen"},
		"span.regex_repeat": {"color": "orangered"},
		"span.regex_any": {"color": "orangered"},
		"code.regex": {"font-size": "80%"},
		"span.regex": {"font-weight": "bold"},
		}

tweaks_sphinx_panels_tabs_styles: MutableMapping[str, dict2css.Style] = {
		".docutils.container": {
				"padding-left": (0, dict2css.IMPORTANT),
				"padding-right": (0, dict2css.IMPORTANT),
				},
		"div.ui.top.attached.tabular.menu.sphinx-menu.docutils.container": {
				"margin-left": (0, dict2css.IMPORTANT),
				"margin-right": (0, dict2css.IMPORTANT),
				},
		}


def copy_asset_files(app: Sphinx, exception: Optional[Exception] = None):
	"""
	Copy additional stylesheets into the HTML build directory.

	:param app: The Sphinx application.
	:param exception: Any exception which occurred and caused Sphinx to abort.
	"""

	if exception:  # pragma: no cover
		return

	if app.builder is None or app.builder.format.lower() != "html":  # pragma: no cover
		return

	extensions_selector = ", ".join([
			"p.sphinx-toolbox-extensions",
			"div.sphinx-toolbox-extensions.highlight-python",
			"div.sphinx-toolbox-extensions.highlight-python div.highlight",
			])

	rest_example_style = {
			"padding-left": "5px",
			"border-style": "dotted",
			"border-width": "1px",
			"border-color": "darkgray",
			}

	style: MutableMapping[str, dict2css.Style] = {
			"p.source-link": {"margin-bottom": 0},
			"p.source-link + hr.docutils": {"margin-top": "10px"},
			extensions_selector: {"margin-bottom": "10px"},
			"div.rest-example.docutils.container": rest_example_style,
			**installation_styles,
			**shields_styles,
			**regex_styles,
			}

	css_static_dir = PathPlus(app.outdir) / "_static" / "css"
	css_static_dir.maybe_make(parents=True)
	dict2css.dump(style, css_static_dir / "sphinx-toolbox.css")


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox._css`.

	:param app: The Sphinx application.
	"""

	app.add_css_file("css/sphinx-toolbox.css")
	app.connect("build-finished", copy_asset_files)

	return {"parallel_read_safe": True}

#!/usr/bin/env python3
#
#  __init__.py
"""
Box of handy tools for Sphinx.
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

# 3rd party
from sphinx.application import Sphinx

# this package
from sphinx_toolbox import (  # noqa: F401
		assets,
		code,
		config,
		confval,
		installation,
		issues,
		rest_example,
		shields,
		source,
		utils,
		wikipedia
		)
from sphinx_toolbox.cache import cache  # noqa: F401

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"

__license__: str = "MIT License"
__version__: str = "2.11.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["setup"]


def setup(app: Sphinx) -> "utils.SphinxExtMetadata":
	"""
	Setup :mod:`sphinx_toolbox`.

	:param app: The Sphinx application.
	"""

	# Ensure dependencies are set up
	app.setup_extension("sphinx.ext.viewcode")
	app.setup_extension("sphinx_toolbox.github")

	app.connect("config-inited", config.validate_config, priority=850)

	# Setup standalone extensions
	app.setup_extension("sphinx_toolbox.assets")
	app.setup_extension("sphinx_toolbox.changeset")
	app.setup_extension("sphinx_toolbox.code")
	app.setup_extension("sphinx_toolbox.collapse")
	app.setup_extension("sphinx_toolbox.confval")
	app.setup_extension("sphinx_toolbox.decorators")
	app.setup_extension("sphinx_toolbox.formatting")
	app.setup_extension("sphinx_toolbox.installation")
	app.setup_extension("sphinx_toolbox.issues")
	app.setup_extension("sphinx_toolbox.latex")
	app.setup_extension("sphinx_toolbox.rest_example")
	app.setup_extension("sphinx_toolbox.shields")
	app.setup_extension("sphinx_toolbox.sidebar_links")
	app.setup_extension("sphinx_toolbox.source")
	app.setup_extension("sphinx_toolbox.wikipedia")
	app.setup_extension("sphinx_toolbox.more_autodoc.autoprotocol")
	app.setup_extension("sphinx_toolbox.more_autodoc.autotypeddict")
	app.setup_extension("sphinx_toolbox.more_autodoc.autonamedtuple")

	# Hack to get the docutils tab size, as there doesn't appear to be any other way
	app.setup_extension("sphinx_toolbox.tweaks.tabsize")

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

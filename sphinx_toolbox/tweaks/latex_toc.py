#!/usr/bin/env python3
#
#  latex_toc.py
"""
Adjusts the default LaTeX output as follows:

* The captions from ``toctree`` directives are converted into document parts.
* The PDF outline has the correct hierarchy, including having the indices as top-level elements.

.. versionadded:: 2.1.0
.. extensions:: sphinx_toolbox.tweaks.latex_toc

.. versionchanged:: 3.0.0

	The functionality has moved to :mod:`sphinx_toolbox.latex.toc`.
	Please use that extension instead.

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

# stdlib

# 3rd party
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.latex import use_package
from sphinx_toolbox.utils import Config, SphinxExtMetadata, metadata_add_version

__all__ = ("setup", "configure")


def configure(app: Sphinx, config: Config) -> None:
	"""
	Configure :mod:`sphinx_toolbox.tweaks.latex_toc`.

	:param app: The Sphinx application.
	:param config:
	"""

	use_package("bookmark", config)


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.tweaks.latex_toc`.

	:param app: The Sphinx application.
	"""

	app.setup_extension("sphinx_toolbox.latex.toc")

	return {"parallel_read_safe": True}

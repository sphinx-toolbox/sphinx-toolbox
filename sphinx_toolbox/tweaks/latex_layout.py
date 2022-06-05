#!/usr/bin/env python3
#
#  latex_layout.py
r"""
Makes minor adjustments to the LaTeX layout.

* Increases the whitespace above function signatures by 5px,
  to prevent the function visually merging with the previous one.
* Remove unnecessary indentation and allow "raggedright" for the fields in
  the body of functions, which prevents ugly whitespace and line breaks.
* Disables justification for function signatures.
  This is a backport of changes from Sphinx 4 added in :github:pull:`8997 <sphinx-doc/sphinx>`.

  .. versionadded:: 2.12.0

* With Sphinx 3.5, doesn't add ``\sphinxAtStartPar`` before every paragraph.
  The change in :github:issue:`8781 <sphinx-doc/sphinx>` was to solve an issue with *tables*,
  but it isn't clear why it then gets added for *every* paragraph so this extension removes it.

  .. versionadded:: 2.13.0

* Configures hyperref to apply correct page numbering to the frontmatter.

  .. versionadded:: 2.14.0

* Optionally, configures the ``needspace`` package.

  The :confval:`needspace_amount` option can be set in ``conf.py`` to add the ``\needspace{}`` command
  before each ``addnodes.desc`` node (i.e. a function or class description).
  The amount of space is set by the ``needspace_amount`` option, e.g.:

  .. code-block:: python

      needspace_amount = r"4\baselineskip"

  .. versionadded:: 3.0.0


.. versionadded:: 2.10.0
.. extensions:: sphinx_toolbox.tweaks.latex_layout


.. versionchanged:: 3.0.0

	The functionality has moved to :mod:`sphinx_toolbox.latex.toc`.
	Please use that extension instead.

-----

"""
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

# 3rd party
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ("setup", )


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.tweaks.latex_layout`.

	:param app: The Sphinx application.
	"""

	app.setup_extension("sphinx_toolbox.latex.layout")

	return {"parallel_read_safe": True}

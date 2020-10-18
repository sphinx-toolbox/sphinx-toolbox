#!/usr/bin/env python3
#
#  generic_bases.py
r"""
Modifies :class:`sphinx.ext.autodoc.ClassDocumenter`\'s ``:show-inheritence:`` option
to show generic base classes.

This requires a relatively new version of the :mod:`typing` module that implements ``__orig_bases__``.

.. versionadded:: 1.5.0

.. extensions:: sphinx_toolbox.more_autodoc.generic_bases


Example
--------

.. autoclass:: sphinx_toolbox.more_autodoc.generic_bases.Example


API Reference
-----------------
"""  # noqa: D400
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
import sys
from typing import List, Tuple

# 3rd party
from sphinx.application import Sphinx
from sphinx.ext.autodoc import Documenter
from sphinx.locale import _

# this package
from sphinx_toolbox.more_autodoc.typehints import format_annotation
from sphinx_toolbox.more_autosummary import PatchedAutoSummClassDocumenter
from sphinx_toolbox.utils import SphinxExtMetadata, allow_subclass_add

if sys.version_info >= (3, 8):
	# stdlib
	from typing import get_origin
else:
	# 3rd party
	from typing_inspect import get_origin  # type: ignore

__all__ = ["GenericBasesClassDocumenter", "setup"]


class GenericBasesClassDocumenter(PatchedAutoSummClassDocumenter):
	"""
	Class documenter that adds inheritance info, with support for generics.
	"""

	def add_directive_header(self, sig: str) -> None:
		"""
		Add the directive header.

		:param sig:
		"""

		sourcename = self.get_sourcename()

		if self.doc_as_attr:
			self.directivetype = "attribute"
		Documenter.add_directive_header(self, sig)

		if self.analyzer and '.'.join(self.objpath) in self.analyzer.finals:
			self.add_line("   :final:", sourcename)

		# add inheritance info, if wanted
		if not self.doc_as_attr and self.options.show_inheritance:
			self.add_line('', sourcename)
			bases = []

			if (
					hasattr(self.object, "__orig_bases__") and len(self.object.__orig_bases__)
					and get_origin(self.object.__orig_bases__[0]) is self.object.__bases__[0]
					):
				# Last condition guards against classes that don't directly subclass a Generic.
				bases = [format_annotation(b) for b in self.object.__orig_bases__]

			elif hasattr(self.object, "__bases__") and len(self.object.__bases__):
				bases = [format_annotation(b) for b in self.object.__bases__]

			if bases:
				self.add_line("   " + _("Bases: %s") % ", ".join(bases), sourcename)


def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.generic_bases`.

	:param app: The Sphinx app.

	.. versionadded:: 1.5.0
	"""

	# this package
	from sphinx_toolbox import __version__

	allow_subclass_add(app, GenericBasesClassDocumenter)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}


class Example(List[Tuple[str, float, List[str]]]):
	"""
	An example of :mod:`sphinx_toolbox.tweaks.generic_bases`.
	"""


class Example2(Example):
	"""
	An example of :mod:`sphinx_toolbox.tweaks.generic_bases`.

	This one does not directly subclass a Generic.
	"""

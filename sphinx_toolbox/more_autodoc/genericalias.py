#!/usr/bin/env python3
#
#  genericalias.py
"""
Documenter for alias, which usually manifest as `type aliases`_.

.. _type aliases: https://docs.python.org/3/library/typing.html#type-aliases

.. versionadded:: 0.6.0
.. extensions:: sphinx_toolbox.more_autodoc.genericalias

.. note::

	:mod:`sphinx_toolbox.more_autodoc.genericalias` is only supported on Python 3.7 and above.

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
#  Parts based on https://github.com/sphinx-doc/sphinx
#  |  Copyright (c) 2007-2020 by the Sphinx team (see AUTHORS file).
#  |  BSD Licensed
#  |  All rights reserved.
#  |
#  |  Redistribution and use in source and binary forms, with or without
#  |  modification, are permitted provided that the following conditions are
#  |  met:
#  |
#  |  * Redistributions of source code must retain the above copyright
#  |   notice, this list of conditions and the following disclaimer.
#  |
#  |  * Redistributions in binary form must reproduce the above copyright
#  |   notice, this list of conditions and the following disclaimer in the
#  |   documentation and/or other materials provided with the distribution.
#  |
#  |  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  |  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  |  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  |  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  |  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  |  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  |  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  |  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  |  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  |  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  |  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
from typing import Any

# 3rd party
from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.ext.autodoc import SUPPRESS, Options
from sphinx.ext.autodoc.directive import DocumenterBridge  # noqa: F401
from sphinx.locale import _
from sphinx.util import inspect

# this package
from sphinx_toolbox._data_documenter import DataDocumenter
from sphinx_toolbox.more_autodoc.typehints import format_annotation
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["PrettyGenericAliasDocumenter", "setup"]


class PrettyGenericAliasDocumenter(DataDocumenter):  # pragma: no cover (<Py37)
	"""
	Specialized Documenter subclass for GenericAliases, with prettier output than Sphinx's one.
	"""

	objtype = "genericalias"
	directivetype = "data"
	priority = DataDocumenter.priority + 2

	@classmethod
	def can_document_member(cls, member: Any, membername: str, isattr: bool, parent: Any) -> bool:
		"""
		Called to see if a member can be documented by this documenter.
		"""

		return inspect.isgenericalias(member)

	def add_directive_header(self, sig: str) -> None:
		"""
		Add the directive header and options to the generated content.
		"""

		self.options = Options(self.options)
		self.options["annotation"] = SUPPRESS
		super().add_directive_header(sig)

	def add_content(self, more_content: Any, no_docstring: bool = False):
		"""
		Add the autodocumenter content.

		:param more_content:
		:param no_docstring:
		"""

		name = format_annotation(self.object)
		content = StringList([_("Alias of %s") % name], source='')
		DataDocumenter.add_content(self, content)


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.genericalias`.

	:param app: The Sphinx application.
	"""

	app.setup_extension("sphinx.ext.autodoc")
	app.add_autodocumenter(PrettyGenericAliasDocumenter, override=True)

	return {"parallel_read_safe": True}

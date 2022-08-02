#!/usr/bin/env python3
#
#  __init__.py
"""
Extensions to :mod:`sphinx.ext.autodoc`.

.. versionadded:: 0.6.0
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
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

# 3rd party
from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.ext.autodoc import Documenter

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

if TYPE_CHECKING:
	# 3rd party
	from sphinx.ext.autodoc import ObjectMembers

	ObjectMembers = ObjectMembers
else:
	ObjectMembers = List[Tuple[str, Any]]

__all__ = ("setup", )


def _documenter_add_content(
		self: Documenter,
		more_content: Optional[StringList],
		no_docstring: bool = False,
		) -> None:
	"""
	Add content from docstrings, attribute documentation and user.
	"""

	# set sourcename and add content from attribute documentation
	sourcename = self.get_sourcename()
	if self.analyzer:
		attr_docs = self.analyzer.find_attr_docs()
		if self.objpath:
			key = ('.'.join(self.objpath[:-1]), self.objpath[-1])
			if key in attr_docs:
				no_docstring = True
				# make a copy of docstring for attributes to avoid cache
				# the change of autodoc-process-docstring event.
				docstrings = [list(attr_docs[key])]

				for i, line in enumerate(self.process_doc(docstrings)):
					self.add_line(line, sourcename, i)

	# add content from docstrings
	if not no_docstring:
		docstrings = self.get_doc() or []
		if docstrings is None:
			# Do not call autodoc-process-docstring on get_doc() returns None.
			pass
		else:
			if not docstrings:
				# append at least a dummy docstring, so that the event
				# autodoc-process-docstring is fired and can add some
				# content if desired
				docstrings.append([])
			for i, line in enumerate(self.process_doc(docstrings)):
				self.add_line(line, sourcename, i)

	# add additional content (e.g. from document), if present
	if more_content:
		for line, src in zip(more_content.data, more_content.items):
			self.add_line(line, src[0], src[1])


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc`.

	:param app: The Sphinx application.
	"""

	# Setup sub-extensions
	app.setup_extension("sphinx_toolbox.more_autodoc.augment_defaults")
	app.setup_extension("sphinx_toolbox.more_autodoc.autoprotocol")
	app.setup_extension("sphinx_toolbox.more_autodoc.autotypeddict")
	app.setup_extension("sphinx_toolbox.more_autodoc.autonamedtuple")
	app.setup_extension("sphinx_toolbox.more_autodoc.genericalias")
	app.setup_extension("sphinx_toolbox.more_autodoc.typehints")
	app.setup_extension("sphinx_toolbox.more_autodoc.variables")
	app.setup_extension("sphinx_toolbox.more_autodoc.sourcelink")
	app.setup_extension("sphinx_toolbox.more_autodoc.no_docstring")
	app.setup_extension("sphinx_toolbox.more_autodoc.regex")
	app.setup_extension("sphinx_toolbox.more_autodoc.typevars")
	app.setup_extension("sphinx_toolbox.more_autodoc.overloads")
	app.setup_extension("sphinx_toolbox.more_autodoc.generic_bases")

	return {"parallel_read_safe": True}

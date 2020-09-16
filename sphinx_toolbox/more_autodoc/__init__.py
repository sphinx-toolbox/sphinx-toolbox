#!/usr/bin/env python3
#
#  __init__.py
"""
Extensions to :mod:`sphinx.ext.autodoc`.

.. versionadded:: 0.6.0
"""
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
import warnings
from types import ModuleType
from typing import Any, Dict, List

# 3rd party
import sphinx.ext.autodoc
from sphinx.application import Sphinx

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.utils import flag

__all__ = ["setup"]


def automodule_add_nodocstring(app) -> None:
	"""
	Add the ``:no-docstring:`` option to automodule directives to exclude the docstring from the output.

	:param app: The Sphinx app.
	"""

	sphinx.ext.autodoc.ModuleDocumenter.option_spec["no-docstring"] = flag

	app.setup_extension("sphinx.ext.autodoc")
	app.connect("autodoc-process-docstring", no_docstring_process_docstring, priority=1000)


def no_docstring_process_docstring(
		app: Sphinx,
		what,
		name: str,
		obj,
		options,
		lines: List[str],
		):
	"""
	Process the docstring of a module, and remove its docstring of the ``no-docstring`` flag was set..

	:param app: The Sphinx app
	:param what:
	:param name: The name of the object being documented
	:param obj: The object being documented.
	:param options: Mapping of autodoc options to values.
	:param lines: List of strings representing the current contents of the docstring.
	"""

	if isinstance(obj, ModuleType):
		no_docstring = options.get("no-docstring", False)
		if no_docstring:
			lines.clear()


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc`.

	:param app: The Sphinx app.
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

	automodule_add_nodocstring(app)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

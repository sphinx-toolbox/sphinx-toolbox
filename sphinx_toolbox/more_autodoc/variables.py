#!/usr/bin/env python3
#
#  variables.py
"""
Documenter for module level variables, similar to :rst:dir:`autodata` but
with a different appearance and more customisation options.

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
from typing import Any, Dict, get_type_hints

# 3rd party
from sphinx.application import Sphinx
from sphinx.ext.autodoc import UNINITIALIZED_ATTR, DataDocumenter, Documenter, ModuleLevelDocumenter
from sphinx.util.inspect import object_description, safe_getattr

# this package
from sphinx_toolbox import __version__
from sphinx_toolbox.more_autodoc.typehints import format_annotation

__all__ = ["get_variable_type", "VariableDocumenter", "setup"]

# this package
from sphinx_toolbox.utils import flag


def get_variable_type(documenter: Documenter) -> str:
	"""
	Returns the type annotation for a variable.

	:param documenter:

	:return:
	"""

	# obtain annotation for this data
	try:
		annotations = get_type_hints(documenter.parent)
	except NameError:
		# Failed to evaluate ForwardRef (maybe TYPE_CHECKING)
		annotations = safe_getattr(documenter.parent, '__annotations__', {})
	except TypeError:
		annotations = {}
	except KeyError:
		# a broken class found (refs: https://github.com/sphinx-doc/sphinx/issues/8084)
		annotations = {}
	except AttributeError:
		# AttributeError is raised on 3.5.2 (fixed by 3.5.3)
		annotations = {}

	if documenter.objpath[-1] in annotations:
		return format_annotation(annotations.get(documenter.objpath[-1]))
	else:
		key = ('.'.join(documenter.objpath[:-1]), documenter.objpath[-1])
		if documenter.analyzer and key in documenter.analyzer.annotations:
			return documenter.analyzer.annotations[key]

		else:
			return ''


class VariableDocumenter(DataDocumenter):
	"""
	Specialized Documenter subclass for data items.
	"""

	directivetype = "data"
	objtype = 'variable'
	priority = DataDocumenter.priority + 1
	option_spec = {
			"no-value": flag,
			"no-type": flag,
			"type": str,
			"value": str,
			**DataDocumenter.option_spec,
			}

	def add_directive_header(self, sig: str) -> None:
		sourcename = self.get_sourcename()

		no_value = self.options.get("no-value", False)
		no_type = self.options.get("no-type", False)

		if not self.options.annotation:
			ModuleLevelDocumenter.add_directive_header(self, sig)

			if not no_value:
				if "value" in self.options:
					self.add_line('   :value: ' + self.options["value"], sourcename)
				else:
					try:
						if self.object is not UNINITIALIZED_ATTR:
							objrepr = object_description(self.object)
							self.add_line('   :value: ' + objrepr, sourcename)
					except ValueError:
						pass

				self.add_line('', sourcename)

			if not no_type:
				if "type" in self.options:
					self.add_line('   :Type: ' + self.options["type"], sourcename)
				else:
					line = '   :Type: ' + get_variable_type(self)
					if line != '   :Type: ':
						self.add_line(line, sourcename)

		else:
			super().add_directive_header(sig)


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.genericalias`.

	:param app: The Sphinx app.
	"""

	app.setup_extension("sphinx.ext.autodoc")
	app.add_autodocumenter(VariableDocumenter, override=True)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

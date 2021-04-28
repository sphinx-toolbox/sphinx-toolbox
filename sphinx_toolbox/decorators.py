#!/usr/bin/env python3
#
#  decorators.py
"""
reStructuredText XRef role for decorators.

.. versionadded:: 0.9.0
.. extensions:: sphinx_toolbox.decorators


Usage
------

.. rst:role:: deco

	Adds a cross reference to a decorator, prefixed with an ``@``.

	.. rest-example::

		.. decorator:: my_decorator

			A decorator.

		:deco:`my_decorator`

		:deco:`@my_decorator`

		:deco:`Title <my_decorator>`


API Reference
----------------

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
#  Based on Sphinx
#  Copyright (c) 2007-2020 by the Sphinx team.
#  |  All rights reserved.
#  |
#  |  Redistribution and use in source and binary forms, with or without
#  |  modification, are permitted provided that the following conditions are
#  |  met:
#  |
#  |  * Redistributions of source code must retain the above copyright
#  |    notice, this list of conditions and the following disclaimer.
#  |
#  |  * Redistributions in binary form must reproduce the above copyright
#  |    notice, this list of conditions and the following disclaimer in the
#  |    documentation and/or other materials provided with the distribution.
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
from typing import Tuple, Type  # noqa: F401

# 3rd party
from docutils.nodes import Element
from sphinx.application import Sphinx
from sphinx.domains.python import PyXRefRole
from sphinx.environment import BuildEnvironment

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["PyDecoXRefRole", "setup"]


class PyDecoXRefRole(PyXRefRole):
	"""
	XRef Role for decorators members.
	"""

	def process_link(  # noqa D102
		self,
		env: BuildEnvironment,
		refnode: Element,
		has_explicit_title: bool,
		title: str,
		target: str,
		) -> Tuple[str, str]:
		"""
		Called after parsing title and target text, and creating the reference node (given in ``refnode``).

		This method can alter the reference node and must return a new (or the same) ``(title, target)`` tuple.

		:param env:
		:param refnode:
		:param has_explicit_title:
		:param title:
		:param target:
		"""

		target = target.lstrip('@')

		title, target = super().process_link(
			env=env,
			refnode=refnode,
			has_explicit_title=has_explicit_title,
			title=title,
			target=target,
			)

		if not has_explicit_title and not title.startswith('@'):
			title = f"@{title}"

		return title, target


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.decorators`.

	:param app: The Sphinx application.
	"""

	app.add_role_to_domain("py", "deco", PyDecoXRefRole())

	return {"parallel_read_safe": True}

#!/usr/bin/env python3
#
#  augment_defaults.py
"""
Sphinx's autodoc module allows for default options to be set,
and allows for those defaults to be disabled for an auto* directive and different values given instead.

However, it does not appear to be possible to augment the defaults,
such as to globally exclude certain members and then exclude additional members of a single class.

This module monkeypatches in that behaviour.

.. extensions:: sphinx_toolbox.more_autodoc.augment_defaults

.. versionchanged:: 0.6.0

	Moved from :mod:`sphinx_toolbox.autodoc_augment_defaults`.
"""  # noqa D400
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
from typing import Any, Dict, List, Type

# 3rd party
import sphinx.ext.autodoc.directive
from docutils.utils import assemble_option_dict
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.errors import ExtensionError
from sphinx.ext.autodoc import Documenter, Options

# this package
import sphinx_toolbox
from sphinx_toolbox.utils import SphinxExtMetadata

__all__ = ["process_documenter_options", "setup"]


def process_documenter_options(
		documenter: Type[Documenter],
		config: Config,
		options: Dict,
		) -> Options:
	"""
	Recognize options of Documenter from user input.

	:param documenter:
	:param config:
	:param options:
	"""

	for name in sphinx.ext.autodoc.directive.AUTODOC_DEFAULT_OPTIONS:
		if name not in documenter.option_spec:  # pragma: no cover
			continue
		else:
			negated = options.pop("no-" + name, True) is None

			if name in config.autodoc_default_options and not negated:
				default_value = config.autodoc_default_options[name]
				existing_value = options.get(name, None)
				values: List[str] = [v for v in [default_value, existing_value] if v not in {None, True, False}]

				if values:
					options[name] = ','.join(values)
				else:
					options[name] = None  # pragma: no cover

	return Options(assemble_option_dict(options.items(), documenter.option_spec))


def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.more_autodoc.augment_defaults`.

	:param app: The Sphinx app.
	"""

	if "sphinx.ext.autodoc" in app.extensions:
		raise ExtensionError(
				"'sphinx_toolbox.more_autodoc.augment_defaults' must be loaded before 'sphinx.ext.autodoc."
				)

	sphinx.ext.autodoc.directive.process_documenter_options = process_documenter_options

	app.setup_extension("sphinx.ext.autodoc")

	return {"version": sphinx_toolbox.__version__, "parallel_read_safe": True}

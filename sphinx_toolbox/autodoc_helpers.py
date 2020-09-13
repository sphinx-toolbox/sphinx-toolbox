#!/usr/bin/env python3
#
#  autodoc_helpers.py
"""
Helpers for writing extensions to autodoc.

.. versionadded:: 0.2.0

.. deprecated:: 0.6.0

	Use :mod:`sphinx_toolbox.more_autodoc.utils` instead.

.. versionremoved:: 1.0.0
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

# stdlib
import warnings

# this package
from sphinx_toolbox.more_autodoc.utils import begin_generate, filter_members_warning, unknown_module_warning

__all__ = ["begin_generate", "unknown_module_warning", "filter_members_warning"]

warnings.warn(
		"Importing from 'sphinx_toolbox.autodoc_helpers' is deprecated since 0.6.0 and "
		"the module will be removed in 1.0.0.\nImport from 'sphinx_toolbox.more_autodoc.utils' instead.",
		DeprecationWarning,
		)

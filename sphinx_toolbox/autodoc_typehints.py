#!/usr/bin/env python3
#
#  autodoc_typehints.py
"""
| Enhanced version of `sphinx-autodoc-typehints <https://pypi.org/project/sphinx-autodoc-typehints/>`_.
| Copyright (c) Alex Grönholm

.. versionadded:: 0.4.0

.. deprecated:: 0.6.0

	Use :mod:`sphinx_toolbox.more_autodoc.typehints` instead.

.. versionremoved:: 1.0.0
"""
#
#  Copyright (c) Alex Grönholm
#  Changes copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
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
from sphinx_toolbox.more_autodoc.typehints import (
		Module,
		_docstring_class_hook,
		_docstring_property_hook,
		backfill_type_hints,
		builder_ready,
		docstring_hooks,
		format_annotation,
		get_all_type_hints,
		get_annotation_args,
		get_annotation_class_name,
		get_annotation_module,
		load_args,
		process_docstring,
		process_signature,
		serialise,
		setup,
		split_type_comment_args
		)

__all__ = [
		"Module",
		"get_annotation_module",
		"get_annotation_class_name",
		"get_annotation_args",
		"format_annotation",
		"process_signature",
		"get_all_type_hints",
		"backfill_type_hints",
		"load_args",
		"split_type_comment_args",
		"process_docstring",
		"builder_ready",
		"docstring_hooks",
		]

warnings.warn(
		"Importing from 'sphinx_toolbox.autodoc_typehints' is deprecated since 0.6.0 and "
		"the module will be removed in 1.0.0.\nImport from 'sphinx_toolbox.more_autodoc.typehints' instead.",
		DeprecationWarning,
		)

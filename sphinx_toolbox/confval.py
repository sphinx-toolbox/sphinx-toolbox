#!/usr/bin/env python3
#
#  confval.py
"""
The confval directive and role for configuration values.

.. extensions:: sphinx_toolbox.confval

Usage
-------

.. rst:directive:: .. confval:: [name]

	Used to document a configuration value.

	.. rst:directive:option:: type
		:type: string

		Indicates the configuration value's type.

	.. rst:directive:option:: required
		:type: flag

		Indicates the whether the configuration value is required.

	.. rst:directive:option:: default
		:type: string

		Indicates the default value.


	**Example:**

	.. rest-example::

		.. confval:: demo
			:type: string
			:default: ``"Hello World"``
			:required: False



.. rst:role:: confval

	Role that provides a cross-reference to a :rst:dir:`confval` directive.

	**Example:**

	.. rest-example::

		:confval:`demo`



API Reference
--------------

"""
#
#  Copyright © 2020 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Based on https://github.com/readthedocs/sphinx_rtd_theme/blob/master/docs/conf.py
#  Copyright (c) 2013-2018 Dave Snider, Read the Docs, Inc. & contributors
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
from typing import List

# 3rd party
from docutils.nodes import Node
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from domdf_python_tools.utils import strtobool
from sphinx.application import Sphinx
from sphinx.domains import ObjType
from sphinx.domains.std import GenericObject, StandardDomain
from sphinx.errors import ExtensionError
from sphinx.roles import XRefRole

# this package
from sphinx_toolbox.utils import OptionSpec, SphinxExtMetadata

__all__ = ["ConfigurationValue", "register_confval", "setup"]


class ConfigurationValue(GenericObject):
	"""
	The confval directive.

	.. versionchanged:: 1.1.0

		The formatting of the type, required and default options can be customised
		using the ``self.format_*`` methods.
	"""

	option_spec: OptionSpec = {  # type: ignore
		"type": directives.unchanged_required,
		"required": directives.unchanged_required,
		"default": directives.unchanged_required,
		}

	def run(self) -> List[Node]:
		"""
		Process the content of the directive.
		"""

		content = []

		if "type" in self.options:
			content.append(f"| **Type:** {self.format_type(self.options['type'])}")
		if "required" in self.options:
			content.append(f"| **Required:** ``{self.format_required(self.options['required'])}``")
		if "default" in self.options:
			content.append(f"| **Default:** {self.format_default(self.options['default'])}")

		self.content = StringList(['', *content, '', *self.content])

		return super().run()

	def format_type(self, the_type: str) -> str:
		"""
		Formats the ``:type:`` option.

		:param the_type:

		:rtype:

		.. versionadded:: 1.1.0
		"""

		return the_type

	def format_required(self, required: str) -> bool:
		"""
		Formats the ``:required:`` option.

		:param required:

		:rtype:

		.. versionadded:: 1.1.0
		"""

		return strtobool(required)

	def format_default(self, default: str) -> str:
		"""
		Formats the ``:default:`` option.

		:param default:

		:rtype:

		.. versionadded:: 1.1.0
		"""

		return default


def register_confval(app: Sphinx, override: bool = False) -> None:
	"""
	Create and register the ``confval`` role and directive.

	:param app: The Sphinx app.
	:param override:
	"""

	if "std" not in app.registry.domains:
		app.add_domain(StandardDomain)  # pragma: no cover

	name = "confval"

	app.registry.add_directive_to_domain("std", name, ConfigurationValue)
	app.registry.add_role_to_domain("std", name, XRefRole())

	object_types = app.registry.domain_object_types.setdefault("std", {})

	if name in object_types and not override:  # pragma: no cover
		raise ExtensionError(f"The {name!r} object_type is already registered")

	object_types[name] = ObjType(name, name)


def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.confval`.

	:param app: The Sphinx app.

	.. versionadded:: 0.7.0
	"""

	# this package
	from sphinx_toolbox import __version__

	register_confval(app)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

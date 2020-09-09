#!/usr/bin/env python3
#
#  confval.py
"""
The confval directive and role for configuration values.
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
from typing import Any, Callable, List, Mapping

# 3rd party
from docutils.nodes import Node
from docutils.parsers.rst import directives
from docutils.statemachine import StringList, ViewList
from domdf_python_tools.utils import strtobool
from sphinx.application import Sphinx
from sphinx.domains import ObjType
from sphinx.domains.std import GenericObject, StandardDomain
from sphinx.errors import ExtensionError
from sphinx.roles import XRefRole

# this package
from sphinx_toolbox.utils import OptionSpec

# from sphinx.domains.python import PyField
# from sphinx.util.docfields import Field

__all__ = ["register_confval", "ConfigurationValue"]


class ConfigurationValue(GenericObject):
	"""
	The confval directive.
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
			content.append(f"| **Type:** {self.options['type']}")
		if "required" in self.options:
			content.append(f"| **Required:** ``{strtobool(self.options['required'])}``")
		if "default" in self.options:
			content.append(f"| **Default:** {self.options['default']}")

		self.content = StringList(['', *content, '', *self.content])

		return super().run()


def register_confval(app: Sphinx, override: bool = False) -> None:
	"""
	Create and register the ``confval`` role and directive.

	:param app:
	:param override:
	"""

	if "std" not in app.registry.domains:
		app.add_domain(StandardDomain)
	#
	# type_field = PyField(
	# 		'type',
	# 		label=_('Type'),
	# 		has_arg=False,
	# 		names=('type', ),
	# 		bodyrolename='class',
	# 		)
	#
	# default_field = Field(
	# 		'default',
	# 		label=_('Default'),
	# 		has_arg=False,
	# 		names=('default', ),
	# 		)
	#
	# app.add_object_type(
	# 		'confval',
	# 		'confval',
	# 		objname='configuration value',
	# 		indextemplate='pair: %s; configuration value',
	# 		doc_field_types=[type_field, default_field],
	# 		)

	name = "confval"

	app.registry.add_directive_to_domain("std", name, ConfigurationValue)
	app.registry.add_role_to_domain("std", name, XRefRole())

	object_types = app.registry.domain_object_types.setdefault("std", {})

	if name in object_types and not override:  # pragma: no cover
		raise ExtensionError(f"The {name!r} object_type is already registered")

	object_types[name] = ObjType(name, name)

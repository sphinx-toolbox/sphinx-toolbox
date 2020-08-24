"""
Sphinx's autodoc module allows for default options to be set,
and allows for those defaults to be disabled for an auto* directive and different values given instead.

However, it does not appear to be possible to augment the defaults,
such as to globally exclude certain members and then exclude additional members of a single class.

This module monkeypatches in that behaviour.
"""

# stdlib
from typing import Any, Dict, Type

# 3rd party
import sphinx.ext.autodoc.directive
from docutils.utils import assemble_option_dict
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.ext.autodoc import Documenter, Options


def process_documenter_options(
		documenter: "Type[Documenter]",
		config: Config,
		options: Dict,
		) -> Options:
	"""
	Recognize options of Documenter from user input.

	:param documenter:
	:param config:
	:param options:
	:return:
	"""

	for name in sphinx.ext.autodoc.directive.AUTODOC_DEFAULT_OPTIONS:
		if name not in documenter.option_spec:
			continue
		else:
			negated = options.pop('no-' + name, True) is None
			if name in config.autodoc_default_options and not negated:

				default_value = config.autodoc_default_options[name]
				existing_value = options.get(name, None)

				values = list(filter(None, [default_value, existing_value]))

				if values:
					options[name] = ",".join(values)
				else:
					options[name] = None

	return Options(assemble_option_dict(options.items(), documenter.option_spec))


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup Sphinx Extension.

	:param app:

	:return:
	"""

	sphinx.ext.autodoc.directive.process_documenter_options = process_documenter_options

	return {}

#!/usr/bin/env python3
#
#  config.py
"""
Internal configuration for ``sphinx-toolbox``.
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

# stdlib
from typing import List

# 3rd party
from apeye.requests_url import RequestsURL
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.utils import Config, add_nbsp_substitution

__all__ = ["MissingOptionError", "InvalidOptionError", "validate_config", "ToolboxConfig"]


class MissingOptionError(ValueError):
	"""
	Subclass of :exc:`ValueError` to indicate a missing configuration option.
	"""


class InvalidOptionError(ValueError):
	"""
	Subclass of :exc:`ValueError` to indicate an invalid value for a configuration value.
	"""


class ToolboxConfig(Config):
	"""
	Subclass of :class:`sphinx.config.Config` with type annotations for the
	configuration values added by ``sphinx-toolbox``.

	Depending on the extensions enabled not all of these configuration values will be present.

	Functionally compatible with :class:`sphinx.config.Config`.
	"""  # noqa: D400

	source_link_target: str
	"""
	The target of the source link, either ``'github'`` or ``'sphinx'``.
	Will be lowercase after :func:`~.validate_config` has run.
	"""

	#: The username of the GitHub account that owns the repository this documentation corresponds to.
	github_username: str

	github_repository: str
	"""
	The GitHub repository this documentation corresponds to.

	.. clearpage::
	"""

	#: The complete URL of the repository on GitHub.
	github_url: RequestsURL

	#: The base URL for the source code on GitHub.
	github_source_url: RequestsURL

	#: The base URL for the issues on GitHub.
	github_issues_url: RequestsURL

	#: The base URL for the pull requests on GitHub.
	github_pull_url: RequestsURL

	#: List of required Conda channels.
	conda_channels: List[str]

	#: The directory in which to find assets for the :rst:role:`asset` role.
	assets_dir: str

	docutils_tab_width: int
	"""
	The tab size used by docutils.
	This is usually 8 spaces, but can be configured in the ``docutils.conf`` file.
	"""

	#: The Wikipedia language to use for :rst:role:`wikipedia` roles.
	wikipedia_lang: str

	#: A string of reStructuredText that will be included at the beginning of every source file that is read.
	rst_prolog: str

	#: Document all :class:`typing.TypeVar`\s, even if they have no docstring.
	all_typevars: bool

	no_unbound_typevars: bool
	r"""
	Only document :class:`typing.TypeVar`\s that have a constraint of are bound.

	This option has no effect if :confval:`all_typevars` is False.
	"""


def validate_config(app: Sphinx, config: ToolboxConfig) -> None:
	"""
	Validate the provided configuration values.

	See :class:`~sphinx_toolbox.config.ToolboxConfig` for a list of the configuration values.

	:param app: The Sphinx application.
	:param config:
	:type config: :class:`~sphinx.config.Config`
	"""

	# this package
	from sphinx_toolbox import github, source

	source._configure(app, config)
	github.validate_config(app, config)
	add_nbsp_substitution(config)

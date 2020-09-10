#!/usr/bin/env python3
#
#  config.py
"""
Internal configuration for ``sphinx-toolbox``.
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

# 3rd party
from apeye.url import URL, RequestsURL
from sphinx.application import Sphinx
from sphinx.config import Config

# this package
from sphinx_toolbox.utils import make_github_url

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

	Functionally compatible with :class:`sphinx.config.Config`.
	"""  # noqa: D400

	source_link_target: str
	"""
	The target of the source link, either ``'github'`` or ``'sphinx'``.
	Will be lowercase after :func:`~.validate_config` has run.
	"""

	#: The username of the GitHub account that owns the repository this documentation corresponds to.
	github_username: str

	#: The GitHub repository this documentation corresponds to.
	github_repository: str

	#: The complete URL of the repository on GitHub.
	github_url: RequestsURL

	#: The base URL for the source code on GitHub.
	github_source_url: RequestsURL

	#: The base URL for the issues on GitHub.
	github_issues_url: RequestsURL

	#: The base URL for the pull requests on GitHub.
	github_pull_url: RequestsURL

	docutils_tab_width: int
	"""
	The tab size used by docutils.
	This is usually 8 spaces, but can be configured in the ``docutils.conf`` file.
	"""

	#: The Wikipedia language to use for :rst:role:`wikipedia` roles.
	wikipedia_lang: str


def validate_config(app: Sphinx, config: ToolboxConfig) -> None:
	r"""
	Validate the provided configuration values.

	The Sphinx configuration values are:

	* source_link_target (:class:`str`\) - The target of the source links, either ``'github'`` or ``'sphinx'``.
	  Always lowercase.

	* github_username (:class:`str`\) - The username of the GitHub account that owns the repository this
	  documentation corresponds to.

	* github_repository (:class:`str`\) - The GitHub repository this documentation corresponds to.
	* github_url (:class:`apeye.url.RequestsURL`\) - The URL of the GitHub repository.
	* github_source_url (:class:`apeye.url.RequestsURL`\) - The base URL for the source code on GitHub.
	* github_issues_url (:class:`apeye.url.RequestsURL`\) - The GitHub issues URL for this repository.
	* github_pull_url (:class:`apeye.url.RequestsURL`\) - The GitHub pull requests URL for this repository.
	* conda_channels (:class:`~typing.List`\[:class:`str:`\]) -
	  The conda channels required to install the library from Anaconda.
	* docutils_tab_width (:class:`int`\) - The number of spaces docutils converts a tab into.
	* wikipedia_lang (:class:`str`\) - The Wikipedia language to use for :rst:role:`wikipedia` roles.

	:param app:
	:param config:
	:type config: :class:`~sphinx.config.Config`
	"""

	config.source_link_target = str(config.source_link_target).lower().strip()

	if config.source_link_target not in {"sphinx", "github"}:
		raise InvalidOptionError("Invalid value for 'source_link_target'.")

	if not config.github_username:
		raise MissingOptionError("The 'github_username' option is required.")
	else:
		config.github_username = str(config.github_username)

	if not config.github_repository:
		raise MissingOptionError("The 'github_repository' option is required.")
	else:
		config.github_repository = str(config.github_repository)

	config.github_url = make_github_url(config.github_username, config.github_repository)
	config.github_source_url = config.github_url / "blob" / "master"
	config.github_issues_url = config.github_url / "issues"
	config.github_pull_url = config.github_url / "pull"

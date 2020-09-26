#!/usr/bin/env python3
#
#  github.py
r"""
Extension to provide GitHub related configuration values to other extensions.

.. versionadded:: 1.0.0


Configuration
--------------

.. confval:: github_username
	:type: :class:`str`
	:required: True

	The username of the GitHub account that owns the repository this documentation corresponds to.

.. confval:: github_repository
	:type: :class:`str`
	:required: True

	The GitHub repository this documentation corresponds to.


API Reference
---------------

You probably don't need to use this extension directly, but if you're developing an
extension of your own you can enable it like so:

.. code-block::

	def setup(app: Sphinx) -> Dict[str, Any]:
		app.setup_extension('sphinx_toolbox.github')
		return {}

This will guarantee that the following values will be available via
:attr:`app.config <sphinx.config.Config>`:

* **github_username** (:class:`str`\) -- The username of the GitHub account that owns the repository this documentation corresponds to.
* **github_repository** (:class:`str`\) -- The GitHub repository this documentation corresponds to.
* **github_url** (:class:`apeye.url.RequestsURL`\) -- The complete URL of the repository on GitHub.
* **github_source_url** (:class:`apeye.url.RequestsURL`\) -- The base URL for the source code on GitHub.
* **github_issues_url** (:class:`apeye.url.RequestsURL`\) -- The base URL for the issues on GitHub.
* **github_pull_url** (:class:`apeye.url.RequestsURL`\) -- The base URL for the pull requests on GitHub.

If the user has not provided either ``github_username`` or ``github_repository``
a :exc:`~.MissingOptionError` will be raised.
"""
# 3rd party
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
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.config import MissingOptionError, ToolboxConfig
from sphinx_toolbox.utils import SphinxExtMetadata, make_github_url

__all__ = ["validate_config", "setup"]


def validate_config(app: Sphinx, config: ToolboxConfig):
	r"""
	Validate the provided configuration values.

	See :class:`~sphinx_toolbox.config.ToolboxConfig` for a list of the configuration values.

	:param app: The Sphinx app.
	:param config:
	:type config: :class:`~sphinx.config.Config`
	"""

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


def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.github`.

	:param app: The Sphinx app.

	.. versionadded:: 1.0.0
	"""

	# this package
	from sphinx_toolbox import __version__

	app.connect("config-inited", validate_config, priority=850)

	app.add_config_value("github_username", None, "env", types=[str])
	app.add_config_value("github_repository", None, "env", types=[str])

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

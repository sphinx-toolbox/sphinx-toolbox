#!/usr/bin/env python3
#
#  __init__.py
r"""
Sphinx domain for GitHub.com, and related utilities.

.. versionadded:: 2.4.0

.. extensions:: sphinx_toolbox.github


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


Usage
------


.. rst:role:: github:issue

	Shows a link to the given issue on GitHub.

	If the issue exists, the link has a tooltip that shows the title of the issue.

	**Example**

	.. rest-example::

		:github:issue:`1`

	You can also reference an issue in a different repository by adding the repository name inside ``<>``.

	.. rest-example::

		:github:issue:`7680 <pytest-dev/pytest>`


.. rst:role:: github:pull

	Shows a link to the given pull request on GitHub.

	If the pull requests exists, the link has a tooltip that shows the title of the pull requests.

	**Example**

	.. rest-example::

		:github:pull:`2`

	You can also reference a pull request in a different repository by adding the repository name inside ``<>``.

	.. rest-example::

		:github:pull:`7671 <pytest-dev/pytest>`


.. rst:role:: github:repo

	Shows a link to the given repository on GitHub.

	**Example**

	.. rest-example::

		:github:repo:`sphinx-toolbox/sphinx-toolbox`

	You can also use a different label for the link:.

	.. rest-example::

		See more in the :github:repo:`pytest repository <pytest-dev/pytest>`.


.. rst:role:: github:user

	Shows a link to the given user on GitHub.

	**Example**

	.. rest-example::

		:github:user:`domdfcoding`

	You can also use a different label for the link:.

	.. rest-example::

		See more of my :github:user:`repositories <domdfcoding>`.


.. rst:role:: github:org

	Shows a link to the given organization on GitHub.

	**Example**

	.. rest-example::

		:github:org:`sphinx-toolbox`

	You can also use a different label for the link:.

	.. rest-example::

		See more repositories in the :github:org:`pytest-dev org <pytest-dev>`.


Caching
-----------

HTTP requests to obtain issue/pull request titles are cached for four hours.

To clear the cache manually, run:

.. prompt:: bash

	python3 -m sphinx_toolbox



API Reference
---------------

Enable this extension from your extension's setup function like so:

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
from sphinx.application import Sphinx
from sphinx.domains import Domain
from sphinx.environment import BuildEnvironment

# this package
from sphinx_toolbox.config import MissingOptionError, ToolboxConfig
from sphinx_toolbox.github.issues import IssueNode, depart_issue_node, issue_role, pull_role, visit_issue_node
from sphinx_toolbox.github.repos_and_users import (
		GitHubObjectLinkNode,
		depart_github_object_link_node,
		repository_role,
		user_role,
		visit_github_object_link_node
		)
from sphinx_toolbox.utils import SphinxExtMetadata, make_github_url, metadata_add_version

_ = BuildEnvironment

__all__ = ["GitHubDomain", "validate_config", "setup"]


class GitHubDomain(Domain):
	"""
	Sphinx domain for `GitHub.com <https://github.com>`_.
	"""

	name = "github"
	label = "GitHub"
	roles = {
			"issue": issue_role,  # type: ignore[dict-item]
			"pull": pull_role,  # type: ignore[dict-item]
			"user": user_role,  # type: ignore[dict-item]
			"org": user_role,  # type: ignore[dict-item]
			"repo": repository_role,  # type: ignore[dict-item]
			}


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


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.github`.

	:param app: The Sphinx app.

	.. versionadded:: 1.0.0
	"""

	app.connect("config-inited", validate_config, priority=850)

	app.add_config_value("github_username", None, "env", types=[str])
	app.add_config_value("github_repository", None, "env", types=[str])
	app.add_domain(GitHubDomain)

	# Custom node for issues and PRs
	app.add_node(IssueNode, html=(visit_issue_node, depart_issue_node))
	app.add_node(GitHubObjectLinkNode, html=(visit_github_object_link_node, depart_github_object_link_node))

	return {"parallel_read_safe": True}

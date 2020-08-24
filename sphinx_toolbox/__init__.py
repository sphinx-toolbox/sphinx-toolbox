#!/usr/bin/env python3
#
#  __init__.py
"""
Box of handy tools for Sphinx.
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
from typing import Any, Dict

# 3rd party
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.config import validate_config
from sphinx_toolbox.issues import IssueNode, depart_issue_node, issue_role, pull_role, visit_issue_node
from sphinx_toolbox.source import source_role

__all__ = ["setup"]

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"

__license__: str = "MIT License"
__version__: str = "0.0.0"
__email__: str = "dominic@davis-foster.co.uk"


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup Sphinx Extension.

	:param app:

	:return:
	"""

	# Link to source code
	app.add_role('source', source_role)

	# Link to GH issue
	app.add_role('issue', issue_role)

	# Link to GH pull request
	app.add_role('pr', pull_role)
	app.add_role('pull', pull_role)

	# Custom node for issues and PRs
	app.add_node(IssueNode, html=(visit_issue_node, depart_issue_node))

	# Configuration values.
	# The target for the source link. One of GitHub or Sphinx (GitLab coming soon)
	app.add_config_value("source_link_target", "Sphinx", "env", types=[str])
	# Required if using "GitHub" as source_link_target
	app.add_config_value("github_username", None, "env", types=[str])
	app.add_config_value("github_repository", None, "env", types=[str])

	app.connect('config-inited', validate_config, priority=850)

	return {'version': __version__, 'parallel_read_safe': True}

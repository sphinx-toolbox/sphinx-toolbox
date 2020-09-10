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
from typing import Any, Dict, Union

# 3rd party
from docutils.nodes import document
from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.parsers import RSTParser

# this package
from sphinx_toolbox import code, config, confval, installation, issues, rest_example, shields, source, wikipedia
from sphinx_toolbox.cache import cache
from sphinx_toolbox.issues import get_issue_title

__author__: str = "Dominic Davis-Foster"
__copyright__: str = "2020 Dominic Davis-Foster"

__license__: str = "MIT License"
__version__: str = "0.4.0"
__email__: str = "dominic@davis-foster.co.uk"

__all__ = ["setup"]


def setup(app: Sphinx) -> Dict[str, Any]:
	"""
	Setup Sphinx Extension.

	:param app:

	:return:
	"""

	# Ensure dependencies are set up
	app.setup_extension("sphinx.ext.viewcode")
	app.setup_extension("sphinx_tabs.tabs")
	app.setup_extension("sphinx-prompt")

	# Link to source code
	app.add_role("source", source.source_role)

	# Link to GH issue
	app.add_role("issue", issues.issue_role)

	# Link to GH pull request
	app.add_role("pr", issues.pull_role)
	app.add_role("pull", issues.pull_role)

	# Custom node for issues and PRs
	app.add_node(issues.IssueNode, html=(issues.visit_issue_node, issues.depart_issue_node))

	# Configuration values.
	# The target for the source link. One of GitHub or Sphinx (GitLab coming soon)
	app.add_config_value("source_link_target", "Sphinx", "env", types=[str])

	# Configuration values.
	app.add_config_value("github_username", None, "env", types=[str])
	app.add_config_value("github_repository", None, "env", types=[str])
	app.add_config_value("conda_channels", [], "env", types=[list])
	app.add_config_value("wikipedia_lang", "en", "env")
	app.connect("config-inited", config.validate_config, priority=850)

	# Instructions for installing a python package
	app.add_directive("installation", installation.InstallationDirective)
	app.connect("env-purge-doc", installation.installation_node_purger.purge_nodes)

	# Code block of reST code, and output
	app.add_directive("rest-example", rest_example.reSTExampleDirective)
	app.connect("env-purge-doc", rest_example.rest_example_purger.purge_nodes)

	# Instructions for enabling a sphinx extension
	app.add_directive("extensions", installation.ExtensionsDirective)
	app.connect("env-purge-doc", installation.extensions_node_purger.purge_nodes)

	# Code block with customisable indent size.
	app.add_directive("code-block", code.CodeBlock, override=True)
	app.add_directive("sourcecode", code.CodeBlock, override=True)

	# Shields/badges
	app.add_directive("rtfd-shield", shields.RTFDShield)
	app.add_directive("travis-shield", shields.TravisShield)
	app.add_directive("actions-shield", shields.GitHubActionsShield)
	app.add_directive("requires-io-shield", shields.RequiresIOShield)
	app.add_directive("coveralls-shield", shields.CoverallsShield)
	app.add_directive("codefactor-shield", shields.CodefactorShield)
	app.add_directive("pypi-shield", shields.PyPIShield)
	app.add_directive("github-shield", shields.GitHubShield)
	app.add_directive("maintained-shield", shields.MaintainedShield)
	app.add_directive("pre-commit-shield", shields.PreCommitShield)

	# Confval role and directive
	confval.register_confval(app)

	# Wikipedia xref role
	app.add_role("wikipedia", wikipedia.make_wikipedia_link)

	# Setup standalone extensions
	app.setup_extension("sphinx_toolbox.formatting")
	app.setup_extension("sphinx_toolbox.autoprotocol")

	# Hack to get the docutils tab size, as there doesn't appear to be any other way
	class CustomRSTParser(RSTParser):

		def parse(self, inputstring: Union[str, StringList], document: document) -> None:
			app.config.docutils_tab_width = document.settings.tab_width  # type: ignore
			super().parse(inputstring, document)

	app.add_source_parser(CustomRSTParser, override=True)

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

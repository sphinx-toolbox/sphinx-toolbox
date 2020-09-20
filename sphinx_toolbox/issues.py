#!/usr/bin/env python3
#
#  issues.py
"""
Add links to GitHub issues and Pull Requests.

.. extensions:: sphinx_toolbox.issues


Usage
------

.. rst:role:: issue

	Shows a link to the given issue on GitHub.

	If the issue exists, the link has a tooltip that shows the title of the issue.

	You can also reference an issue in a different repository by adding the repository name inside ``<>``.
	You'll probably want to add some text to tell the user that this issue is from a different project.

	**Example**

	.. rest-example::

		:issue:`1`

		pytest issue :issue:`7680 <pytest-dev/pytest>`


.. rst:role:: pull

	Shows a link to the given pull request on GitHub.

	If the pull requests exists, the link has a tooltip that shows the title of the pull requests.

	You can also reference a pull request in a different repository by adding the repository name inside ``<>``.
	You'll probably want to add some text to tell the user that this pull request is from a different project.

	**Example**

	.. rest-example::

		:pull:`2`

		pytest pull request :issue:`7671 <pytest-dev/pytest>`


The only difference between the :rst:role:`issue` and :rst:role:`pull` roles
is in the URL. GitHub uses the same numbering scheme for issues and
pull requests, and automatically redirects to the pull request if
the user tries to navigate to an issue with that same number.



API Reference
---------------
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
#  Based on pyspecific.py from the Python documentation.
#  Copyright 2008-2014 by Georg Brandl.
#  Licensed under the PSF License 2.0
#
#  Parts of the docstrings based on https://docutils.sourceforge.io/docs/howto/rst-roles.html
#

# stdlib
import warnings
from typing import Dict, List, Optional, Tuple, Union

# 3rd party
from apeye.url import URL
from bs4 import BeautifulSoup  # type: ignore
from docutils import nodes, utils
from docutils.nodes import system_message
from docutils.parsers.rst.states import Inliner
from sphinx.application import Sphinx
from sphinx.util.nodes import split_explicit_title
from sphinx.writers.html import HTMLTranslator

# this package
from sphinx_toolbox.cache import cache
from sphinx_toolbox.utils import SphinxExtMetadata, make_github_url

__all__ = [
		"IssueNode",
		"issue_role",
		"pull_role",
		"visit_issue_node",
		"depart_issue_node",
		"get_issue_title",
		"setup",
		]


class IssueNode(nodes.reference):
	"""
	Docutils Node to represent a link to a GitHub *Issue* or *Pull Request*.

	:param issue_number: The number of the issue or pull request.
	:param refuri: The URL of the issue / pull request on GitHub.
	"""

	has_tooltip: bool
	issue_number: int
	issue_url: str

	def __init__(
			self,
			issue_number: Union[str, int],
			refuri: Union[str, URL],
			**kwargs,
			):
		self.has_tooltip = False
		self.issue_number = int(issue_number)
		self.issue_url = str(refuri)

		super().__init__(f"#{issue_number}", f"#{issue_number}", refuri=str(refuri))

	def copy(self) -> "IssueNode":  # pragma: no cover
		"""
		Return a copy of the :class:`sphinx_toolbox.issues.IssueNode`.
		"""

		# This was required to stop some breakage, but it doesn't seem to run during the tests.
		obj = self.__class__(issue_number=self.issue_number, refuri=self.issue_url)
		obj.document = self.document
		obj.source = self.source
		obj.line = self.line
		return obj


def issue_role(
		name: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict = {},
		content: List[str] = []
		) -> Tuple[List[IssueNode], List[system_message]]:
	"""
	Adds a link to the given issue on GitHub.

	:param name: The local name of the interpreted role, the role name actually used in the document.
	:param rawtext: A string containing the entire interpreted text input, including the role and markup.
	:param text: The interpreted text content.
	:param lineno: The line number where the interpreted text begins.
	:param inliner: The :class:`docutils.parsers.rst.states.Inliner` object that called :func:`~.issue_role`.
		It contains the several attributes useful for error reporting and document tree access.
	:param options: A dictionary of directive options for customization (from the ``role`` directive),
		to be interpreted by the function.
		Used for additional attributes for the generated elements and other functionality.
	:param content: A list of strings, the directive content for customization (from the ``role`` directive).
		To be interpreted by the function.

	:return: A list containing the created node, and a list containing any messages generated during the function.
	"""

	has_t, issue_number, repository = split_explicit_title(text)
	issue_number = utils.unescape(issue_number)

	messages: List[system_message] = []

	if has_t:
		repository_parts = utils.unescape(repository).split("/")
		if len(repository_parts) != 2:
			inliner.document.reporter.warning(f"Invalid repository '{repository}' for issue #{issue_number}.")
			issues_url = inliner.document.settings.env.app.config.github_issues_url
		else:
			repository_url = make_github_url(*repository_parts)
			issues_url = repository_url / "issues"
	else:
		issues_url = inliner.document.settings.env.app.config.github_issues_url

	refnode = IssueNode(issue_number, refuri=issues_url / str(int(issue_number)))

	return [refnode], messages


def pull_role(
		name: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict = {},
		content: List[str] = []
		) -> Tuple[List[IssueNode], List[system_message]]:
	"""
	Adds a link to the given pulll request on GitHub.

	:param name: The local name of the interpreted role, the role name actually used in the document.
	:param rawtext: A string containing the entire interpreted text input, including the role and markup.
	:param text: The interpreted text content.
	:param lineno: The line number where the interpreted text begins.
	:param inliner: The :class:`docutils.parsers.rst.states.Inliner` object that called :func:`~.pull_role`.
		It contains the several attributes useful for error reporting and document tree access.
	:param options: A dictionary of directive options for customization (from the ``role`` directive),
		to be interpreted by the function.
		Used for additional attributes for the generated elements and other functionality.
	:param content: A list of strings, the directive content for customization (from the ``role`` directive).
		To be interpreted by the function.

	:return: A list containing the created node, and a list containing any messages generated during the function.
	"""

	has_t, issue_number, repository = split_explicit_title(text)
	issue_number = utils.unescape(issue_number)

	messages: List[system_message] = []

	if has_t:
		repository_parts = utils.unescape(repository).split("/")
		if len(repository_parts) != 2:
			inliner.document.reporter.warning(
					f"Invalid repository '{repository}' for pull request #{issue_number}."
					)
			pull_url = inliner.document.settings.env.app.config.github_pull_url
		else:
			repository_url = make_github_url(*repository_parts)
			pull_url = repository_url / "pull"
	else:
		pull_url = inliner.document.settings.env.app.config.github_pull_url

	refnode = IssueNode(issue_number, refuri=pull_url / str(int(issue_number)))

	return [refnode], messages


def visit_issue_node(translator: HTMLTranslator, node: IssueNode):
	"""
	Visit an :class:`~.IssueNode`.

	If the node points to a valid issue / pull request,
	add a tooltip giving the title of the issue / pull request and a hyperlink to the page on GitHub.

	:param translator:
	:param node: The node being visited.
	"""

	issue_title = get_issue_title(node.issue_url)

	if issue_title:
		node.has_tooltip = True
		translator.body.append(f'<abbr title="{issue_title}">')
		translator.visit_reference(node)
	else:
		warnings.warn(f"Issue/Pull Request #{node.issue_number} not found.")


def depart_issue_node(translator: HTMLTranslator, node: IssueNode):
	"""
	Depart an :class:`~.IssueNode`.

	:param translator:
	:param node: The node being visited.
	"""

	if node.has_tooltip:
		translator.depart_reference(node)
		translator.body.append("</abbr>")


def get_issue_title(issue_url: str) -> Optional[str]:
	"""
	Returns the title of the issue with the given url,
	or :py:obj:`None` if the issue isn't found.

	:param issue_url:
	"""  # noqa D400

	r = cache.session.get(issue_url)

	if r.status_code == 200:
		soup = BeautifulSoup(r.content, "html5lib")
		return soup.find_all("span", attrs={"class": "js-issue-title"})[0].contents[0].strip().strip()

	return None


def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.issues`.

	:param app: The Sphinx app.

	.. versionadded:: 1.0.0
	"""

	# this package
	from sphinx_toolbox import __version__

	app.setup_extension("sphinx_toolbox.github")

	# Link to GH issue
	app.add_role("issue", issue_role)

	# Link to GH pull request
	app.add_role("pr", pull_role)
	app.add_role("pull", pull_role)

	# Custom node for issues and PRs
	app.add_node(IssueNode, html=(visit_issue_node, depart_issue_node))

	return {
			"version": __version__,
			"parallel_read_safe": True,
			}

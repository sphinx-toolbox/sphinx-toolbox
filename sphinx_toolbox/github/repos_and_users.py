#!/usr/bin/env python3
#
#  repos_and_users.py
"""
Roles and nodes for referencing GitHub repositories and organizations.
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
#  Parts of the docstrings based on https://docutils.sourceforge.io/docs/howto/rst-roles.html
#

# stdlib
from typing import Any, Dict, List, Tuple, Union

# 3rd party
from apeye.url import URL
from bs4 import BeautifulSoup  # type: ignore
from docutils import nodes
from docutils.nodes import system_message
from docutils.parsers.rst.states import Inliner
from sphinx.util.nodes import split_explicit_title
from sphinx.writers.html import HTMLTranslator

# this package
from sphinx_toolbox.utils import GITHUB_COM, make_github_url

__all__ = [
		"GitHubObjectLinkNode",
		"repository_role",
		"user_role",
		"visit_github_object_link_node",
		"depart_github_object_link_node",
		]


class GitHubObjectLinkNode(nodes.reference):
	"""
	Docutils Node to represent a link to a GitHub repository.

	:param repo_name: The full name of the repository, in the form ``owner/name``.
	:param refuri: The URL of the issue / pull request on GitHub.
	"""

	name: str
	url: str

	def __init__(
			self,
			name: str,
			refuri: Union[str, URL],
			**kwargs,
			):
		self.name = str(name)
		self.url = str(refuri)

		super().__init__(self.name, self.name, refuri=self.url)

	def copy(self) -> "GitHubObjectLinkNode":  # pragma: no cover
		"""
		Return a copy of the :class:`sphinx_toolbox.github.repos.GitHubObjectLinkNode`.
		"""

		# This was required to stop some breakage, but it doesn't seem to run during the tests.
		obj = self.__class__(self.name, self.url)
		obj.document = self.document
		obj.source = self.source
		obj.line = self.line
		return obj


def repository_role(
		name: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict[str, Any] = {},
		content: List[str] = []
		) -> Tuple[List[nodes.reference], List[system_message]]:
	"""
	Adds a link to the given repository on GitHub.

	:param name: The local name of the interpreted role, the role name actually used in the document.
	:param rawtext: A string containing the entire interpreted text input, including the role and markup.
	:param text: The interpreted text content.
	:param lineno: The line number where the interpreted text begins.
	:param inliner: The :class:`docutils.parsers.rst.states.Inliner` object that called :func:`~.repository_role`.
		It contains the several attributes useful for error reporting and document tree access.
	:param options: A dictionary of directive options for customization (from the ``role`` directive),
		to be interpreted by the function.
		Used for additional attributes for the generated elements and other functionality.
	:param content: A list of strings, the directive content for customization (from the ``role`` directive).
		To be interpreted by the function.

	:return: A list containing the created node, and a list containing any messages generated during the function.
	"""

	has_t, text, repo_name = split_explicit_title(text)
	repo_name = nodes.unescape(repo_name)
	repository_parts = nodes.unescape(repo_name).split('/')

	messages: List[system_message] = []

	if len(repository_parts) != 2:
		inliner.document.reporter.warning(f"Invalid repository '{repo_name}'.")
		return [], messages

	# refnode: nodes.reference

	if has_t:
		refnode = nodes.reference(
				text,
				text,
				refuri=str(make_github_url(*repository_parts)),
				)

	else:
		refnode = GitHubObjectLinkNode(
				name=repo_name,
				refuri=make_github_url(*repository_parts),
				)

	return [refnode], messages


def user_role(
		name: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict[str, Any] = {},
		content: List[str] = []
		) -> Tuple[List[nodes.reference], List[system_message]]:
	"""
	Adds a link to the given user / organization on GitHub.

	:param name: The local name of the interpreted role, the role name actually used in the document.
	:param rawtext: A string containing the entire interpreted text input, including the role and markup.
	:param text: The interpreted text content.
	:param lineno: The line number where the interpreted text begins.
	:param inliner: The :class:`docutils.parsers.rst.states.Inliner` object that called :func:`~.user_role`.
		It contains the several attributes useful for error reporting and document tree access.
	:param options: A dictionary of directive options for customization (from the ``role`` directive),
		to be interpreted by the function.
		Used for additional attributes for the generated elements and other functionality.
	:param content: A list of strings, the directive content for customization (from the ``role`` directive).
		To be interpreted by the function.

	:return: A list containing the created node, and a list containing any messages generated during the function.
	"""

	has_t, text, username = split_explicit_title(text)
	username = nodes.unescape(username)

	messages: List[system_message] = []

	if has_t:
		refnode = nodes.reference(
				text,
				text,
				refuri=str(GITHUB_COM / username),
				)

	else:
		refnode = GitHubObjectLinkNode(
				name=f"@{username}",
				refuri=GITHUB_COM / username,
				)

	return [refnode], messages


def visit_github_object_link_node(translator: HTMLTranslator, node: GitHubObjectLinkNode):
	"""
	Visit a :class:`~.GitHubObjectLinkNode`.

	:param translator:
	:param node: The node being visited.
	"""

	translator.body.append(f'<b class="github-object">')
	translator.visit_reference(node)


def depart_github_object_link_node(translator: HTMLTranslator, node: GitHubObjectLinkNode):
	"""
	Depart an :class:`~.GitHubObjectLinkNode`.

	:param translator:
	:param node: The node being visited.
	"""

	translator.depart_reference(node)
	translator.body.append("</b>")

#!/usr/bin/env python3
#
#  utils.py
"""
General utility functions.
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
import functools
from typing import Any, Callable, Iterable, Mapping

# 3rd party
from apeye.url import RequestsURL
from docutils.nodes import Node
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment

__all__ = ["make_github_url", "GITHUB_COM", "flag", "word_join", "Purger", "OptionSpec"]

#: Instance of :class:`apeye.url.RequestsURL` that points to the GitHub website.
GITHUB_COM = RequestsURL("https://github.com")

# Type hint for the ``option_spec`` variable of Docutils directives.
OptionSpec = Mapping[str, Callable[[str], Any]]


@functools.lru_cache()
def make_github_url(username: str, repository: str) -> RequestsURL:
	"""
	Construct a URL to a GitHub repository from a username and repository name.

	:param username: The username of the GitHub account that owns the repository.
	:param repository: The name of the repository.
	"""

	return GITHUB_COM / username / repository


def flag(argument: Any) -> bool:
	"""
	Check for a valid flag option (no argument) and return :py:obj:`True`.

	Used in the ``option_spec`` of directives.

	.. seealso::

		:class:`docutils.parsers.rst.directives.flag`, which returns :py:obj:`None` instead of :py:obj:`True`.

	:raises: :exc:`ValueError` if an argument is given.
	"""

	if argument and argument.strip():
		raise ValueError(f"No argument is allowed; {argument!r} supplied")
	else:
		return True


def word_join(iterable: Iterable[str], use_repr: bool = False, oxford: bool = False) -> str:
	"""
	Join the given list of strings in a natural manner, with 'and' to join the last two elements.

	:param iterable:
	:param use_repr: Whether to join the ``repr`` of each object.
	:param oxford: Whether to use an oxford comma when joining the last two elements.
		Always :py:obj:`False` if there are less than three elements.
	"""

	if use_repr:
		words = [repr(w) for w in iterable]
	else:
		words = list(iterable)

	if len(words) == 0:
		return ''
	elif len(words) == 1:
		return words[0]
	elif len(words) == 2:
		return " and ".join(words)
	else:
		if oxford:
			return ", ".join(words[:-1]) + f", and {words[-1]}"
		else:
			return ", ".join(words[:-1]) + f" and {words[-1]}"


class Purger:
	"""
	Class to purge redundant nodes.

	:param attr_name: The name of the build environment's attribute that stores the list of nodes,
		e.g. ``all_installation_nodes``.
	"""

	def __init__(self, attr_name: str):
		self.attr_name = str(attr_name)

	def purge_nodes(self, app: Sphinx, env: BuildEnvironment, docname: str) -> None:
		"""
		Remove all redundant :class:`sphinx_toolbox.installation.InstallationDirective` nodes.

		:param app:
		:param env:
		:param docname: The name of the document to remove nodes for.
		"""

		if not hasattr(env, self.attr_name):
			return

		all_nodes = [
				todo for todo in getattr(env, self.attr_name) if todo["docname"] != docname
				]  # pragma: no cover
		setattr(env, self.attr_name, all_nodes)  # pragma: no cover

	def add_node(self, env: BuildEnvironment, node: Node, targetnode: Node, lineno: int):
		"""
		Add a node.

		:param env:
		:param node:
		:param targetnode:
		:param lineno:
		"""

		if not hasattr(env, self.attr_name):
			setattr(env, self.attr_name, [])

		all_nodes = getattr(env, self.attr_name)

		all_nodes.append({
				"docname": env.docname,
				"lineno": lineno,
				"installation_node": node.deepcopy(),
				"target": targetnode,
				})

#!/usr/bin/env python3
#
#  wikipedia.py
"""
Sphinx extension to create links to Wikipedia articles.

.. versionadded:: 0.2.0
.. extensions:: sphinx_toolbox.wikipedia


Configuration
--------------

.. confval:: wikipedia_lang
	:type: :class:`str`
	:required: False
	:default: ``'en'``

	The Wikipedia language to use for :rst:role:`wikipedia` roles.

	.. versionadded:: 0.2.0


Usage
------

.. rst:role:: wikipedia

	Role which shows a link to the given article on Wikipedia.

	The title and language can be customised.


	**Example**

	.. rest-example::

		:wikipedia:`Sphinx`

		:wikipedia:`mythical creature <Sphinx>`

		:wikipedia:`Answer to the Ultimate Question of Life, the Universe, and Everything <:de:42 (Antwort)>`

	.. only:: html

		.. rest-example::

			:wikipedia:`:zh:斯芬克斯`


API Reference
----------------
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
#  Based on https://github.com/quiver/sphinx-ext-wikipedia
#  BSD Licensed
#
#  Parts of the docstrings based on https://docutils.sourceforge.io/docs/howto/rst-roles.html
#

# stdlib
import re
from typing import Dict, List, Tuple
from urllib.parse import quote

# 3rd party
from apeye.url import URL
from docutils import nodes
from docutils.nodes import system_message
from docutils.parsers.rst.states import Inliner
from sphinx.application import Sphinx
from sphinx.util.nodes import split_explicit_title

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["make_wikipedia_link", "setup"]

base_url = "https://%s.wikipedia.org/wiki"
_wiki_lang_re = re.compile(":(.*?):(.*)")


def _get_wikipedia_lang(inliner: Inliner):  # pragma: no cover
	return inliner.document.settings.env.config.wikipedia_lang


def make_wikipedia_link(
		name: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict = {},
		content: List[str] = []
		) -> Tuple[List[nodes.reference], List[system_message]]:
	"""
	Adds a link to the given article on :wikipedia:`Wikipedia`.

	:param name: The local name of the interpreted role, the role name actually used in the document.
	:param rawtext: A string containing the entire interpreted text input, including the role and markup.
	:param text: The interpreted text content.
	:param lineno: The line number where the interpreted text begins.
	:param inliner: The :class:`docutils.parsers.rst.states.Inliner` object that called :func:`~.source_role`.
		It contains the several attributes useful for error reporting and document tree access.
	:param options: A dictionary of directive options for customization (from the ``role`` directive),
		to be interpreted by the function.
		Used for additional attributes for the generated elements and other functionality.
	:param content: A list of strings, the directive content for customization (from the ``role`` directive).
		To be interpreted by the function.

	:return: A list containing the created node, and a list containing any messages generated during the function.
	"""

	text = nodes.unescape(text)
	has_explicit, title, target = split_explicit_title(text)

	m = _wiki_lang_re.match(target)

	if m:
		lang, target = m.groups()
		if not has_explicit:
			title = target
	else:
		lang = _get_wikipedia_lang(inliner)

	ref = URL(base_url % lang) / quote(target.replace(' ', '_'), safe='')

	node = nodes.reference(rawtext, title, refuri=str(ref), **options)
	return [node], []


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.wikipedia`.

	.. versionadded:: 1.0.0

	:param app: The Sphinx application.
	"""

	app.add_role("wikipedia", make_wikipedia_link)
	app.add_config_value("wikipedia_lang", "en", "env", [str])

	return {"parallel_read_safe": True}

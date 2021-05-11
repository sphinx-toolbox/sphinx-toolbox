#!/usr/bin/env python3
#
#  assets.py
"""
Role to provide a link to open a file within the web browser, rather than downloading it.

.. versionadded:: 0.5.0
.. extensions:: sphinx_toolbox.assets
.. TODO:: Handle non-HTML builders

	Perhaps just put a message to see the online documentation?

Usage
------

.. rst:role:: asset

	Adds a link to a local file that can be viewed within the web browser.
	The file will be copied from the directory set in :confval:`assets_dir` to ``/_assets`` in the HTML output.

	This is similar to the :rst:role:`download` role, but that role will download the file to the user's computer instead.
	This role may be useful for PDFs, which most web browsers can display.

	If the file can't be found an error will be shown in the build output:

	.. code-block:: text

		<page where the error occurred>: Asset file '<missing asset file name>' not found.


	.. versionadded:: 0.5.0

	**Asset**

	.. rest-example::

		:asset:`hello_world.txt`

		:asset:`hello_world <hello_world.txt>`

	**Download**

	.. rest-example::

		:download:`hello_world.txt <../assets/hello_world.txt>`


Configuration
---------------

.. confval:: assets_dir
	:type: :class:`str`
	:required: False
	:default: ``'./assets'``

	The directory in which to find assets for the :rst:role:`asset` role.

	.. versionadded:: 0.5.0


API Reference
---------------

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
import pathlib
import posixpath
import shutil
from typing import Dict, List, Sequence, Tuple

# 3rd party
from consolekit.terminal_colours import Fore
from docutils import nodes
from docutils.nodes import system_message
from docutils.parsers.rst.states import Inliner
from domdf_python_tools.paths import PathPlus
from domdf_python_tools.utils import stderr_writer
from sphinx.application import Sphinx
from sphinx.util import split_explicit_title
from sphinx.writers.html import HTMLTranslator

__all__ = [
		"asset_role",
		"AssetNode",
		"visit_asset_node",
		"depart_asset_node",
		"setup",
		]

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version


class AssetNode(nodes.reference):
	"""
	Node representing a link to an asset.
	"""


def asset_role(
		name: str,
		rawtext: str,
		text: str,
		lineno: int,
		inliner: Inliner,
		options: Dict = {},
		content: List[str] = []
		) -> Tuple[Sequence[AssetNode], List[system_message]]:
	"""
	Adds a link to an asset.

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

	has_t, title, target = split_explicit_title(text)
	title = nodes.unescape(title)
	target = nodes.unescape(target)

	if not has_t:
		if target.startswith('~'):
			target = target[1:]
			title = pathlib.PurePosixPath(text[1:]).name

	app = inliner.document.settings.env.app
	base = app.config.assets_dir
	node = AssetNode(rawtext, title, refuri=target, source_file=PathPlus(base) / target, **options)

	return [node], []


def visit_asset_node(translator: HTMLTranslator, node: AssetNode):
	"""
	Visit an :class:`~.AssetNode`.

	:param translator:
	:param node: The node being visited.
	"""

	if not hasattr(translator, "_asset_node_seen_files"):
		# Files that have already been seen
		translator._asset_node_seen_files = []  # type: ignore

	assets_out_dir = PathPlus(translator.builder.outdir) / "_assets"
	assets_out_dir.maybe_make(parents=True)

	source_file = PathPlus(translator.builder.confdir) / node["source_file"]

	if source_file not in translator._asset_node_seen_files and source_file.is_file():  # type: ignore
		# Avoid unnecessary copies of potentially large files.
		translator._asset_node_seen_files.append(source_file)  # type: ignore
		shutil.copy2(source_file, assets_out_dir)
	elif not source_file.is_file():
		stderr_writer(Fore.RED(f"{translator.builder.current_docname}: Asset file '{source_file}' not found."))
		translator.context.append('')
		return

	# Create the HTML
	current_uri = (pathlib.PurePosixPath('/') / translator.builder.current_docname).parent
	refuri = posixpath.relpath(f"/_assets/{node['refuri']}", str(current_uri))
	translator.body.append(f'<a class="reference external" href="{refuri}")/">')
	translator.context.append("</a>")


def depart_asset_node(translator: HTMLTranslator, node: AssetNode):
	"""
	Depart an :class:`~.AssetNode`.

	:param translator:
	:param node: The node being visited.
	"""

	translator.body.append(translator.context.pop())


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.assets`.

	.. versionadded:: 1.0.0

	:param app: The Sphinx application.
	"""

	app.add_role("asset", asset_role)
	app.add_config_value("assets_dir", "./assets", "env", [str])
	app.add_node(AssetNode, html=(visit_asset_node, depart_asset_node))

	return {"parallel_read_safe": True}

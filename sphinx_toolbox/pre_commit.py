#!/usr/bin/env python3
#
#  pre_commit.py
"""
Sphinx extension to show examples of ``.pre-commit-config.yaml`` configuration.

.. versionadded:: 1.6.0
.. extensions:: sphinx_toolbox.pre_commit


Usage
------

.. rst:directive:: pre-commit

	Directive which shows an example snippet of ``.pre-commit-config.yaml``.

	.. rst:directive:option:: rev
		:type: string

		The revision or tag to clone at.

	.. rst:directive:option:: hooks
		:type: comma separated list

		A list of hooks IDs to document.

		If not given the hooks will be parsed from ``.pre-commit-hooks.yaml``.

	.. rst:directive:option:: args
		:type: comma separated list

		A list arguments that should or can be provided to the first hook ID.

		.. versionadded:: 1.7.2


	:bold-title:`Example`

	.. rest-example::

		.. pre-commit::
			:rev: v0.0.4
			:hooks: some-hook,some-other-hook

.. clearpage::

.. rst:directive:: .. pre-commit:flake8:: version

	Directive which shows an example snippet of ``.pre-commit-config.yaml`` for a flake8 plugin.

	The directive takes a single argument -- the version of the flake8 plugin to install from PyPI.

	.. rst:directive:option:: flake8-version
		:type: string

		The version of flake8 to use. Default ``3.8.4``.

	.. rst:directive:option:: plugin-name
		:type: string

		The name of the plugin to install from PyPI. Defaults to the repository name.

	:bold-title:`Example`

	.. rest-example::

		.. pre-commit:flake8:: 0.0.4

	.. versionchanged:: 2.8.0  The repository URL now points to GitHub.

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

# stdlib
import re
import warnings
from io import StringIO
from textwrap import indent
from typing import Any, List, Sequence

# 3rd party
import sphinx.util.docutils
from docutils import nodes
from docutils.statemachine import StringList
from domdf_python_tools.paths import PathPlus
from ruamel.yaml import YAML
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from typing_extensions import TypedDict

# this package
from sphinx_toolbox.utils import Purger, SphinxExtMetadata, make_github_url, metadata_add_version

__all__ = [
		"pre_commit_node_purger",
		"pre_commit_f8_node_purger",
		"parse_hooks",
		"PreCommitDirective",
		"Flake8PreCommitDirective",
		"setup",
		]

pre_commit_node_purger = Purger("all_pre_commit_nodes")
pre_commit_f8_node_purger = Purger("all_pre_commit_f8_nodes")


def parse_hooks(hooks: str) -> List[str]:
	"""
	Parses the comma, semicolon and/or space delimited list of hook IDs.

	:param hooks:
	"""

	return list(filter(None, re.split("[,; ]", hooks)))


class _BaseHook(TypedDict):
	id: str  # noqa: A003  # pylint: disable=redefined-builtin


class _Hook(_BaseHook, total=False):
	args: List[str]


class _BaseConfig(TypedDict):
	repo: str


class _Config(_BaseConfig, total=False):
	rev: str
	hooks: List[_Hook]


class PreCommitDirective(SphinxDirective):
	"""
	A Sphinx directive for documenting pre-commit hooks.

	.. clearpage::
	"""

	has_content: bool = False
	option_spec = {
			"rev": str,  # the revision or tag to clone at.
			"hooks": parse_hooks,
			"args": parse_hooks,
			}

	def run(self) -> Sequence[nodes.Node]:  # type: ignore
		"""
		Process the content of the directive.
		"""

		if "hooks" in self.options:
			hooks = self.options["hooks"]
		else:
			cwd = PathPlus.cwd()

			for directory in (cwd, *cwd.parents):
				hook_file = directory / ".pre-commit-hooks.yaml"
				if hook_file.is_file():
					hooks_dict = YAML(typ="safe", pure=True).load(hook_file.read_text())
					hooks = [h["id"] for h in hooks_dict]
					break
			else:
				warnings.warn("No hooks specified and no .pre-commit-hooks.yaml file found.")
				return []

		repo = make_github_url(self.env.config.github_username, self.env.config.github_repository)
		config: _Config = {"repo": str(repo)}

		if "rev" in self.options:
			config["rev"] = self.options["rev"]

		config["hooks"] = [{"id": hook_name} for hook_name in hooks]

		if "args" in self.options:
			config["hooks"][0]["args"] = self.options["args"]

		targetid = f'pre-commit-{self.env.new_serialno("pre-commit"):d}'
		targetnode = nodes.section(ids=[targetid])

		yaml_dumper = YAML()
		yaml_dumper.default_flow_style = False

		yaml_output_stream = StringIO()
		yaml_dumper.dump([config], stream=yaml_output_stream)

		yaml_output = yaml_output_stream.getvalue()

		if not yaml_output:
			return []

		content = f".. code-block:: yaml\n\n{indent(yaml_output, '    ')}\n\n"
		view = StringList(content.split('\n'))
		pre_commit_node = nodes.paragraph(rawsource=content)
		self.state.nested_parse(view, self.content_offset, pre_commit_node)

		pre_commit_node_purger.add_node(self.env, pre_commit_node, targetnode, self.lineno)

		return [pre_commit_node]


class Flake8PreCommitDirective(SphinxDirective):
	"""
	A Sphinx directive for documenting flake8 plugins' pre-commit hooks.
	"""

	has_content: bool = False
	option_spec = {
			"flake8-version": str,
			"plugin-name": str,  # defaults to repository name
			}
	required_arguments = 1  # the plugin version

	def run(self) -> Sequence[nodes.Node]:  # type: ignore
		"""
		Process the content of the directive.
		"""

		plugin_name = self.options.get("plugin-name", self.env.config.github_repository)
		flake8_version = self.options.get("flake8-version", "3.8.4")

		config = {
				"repo": "https://github.com/pycqa/flake8",
				"rev": flake8_version,
				"hooks": [{"id": "flake8", "additional_dependencies": [f"{plugin_name}=={self.arguments[0]}"]}]
				}

		targetid = f'pre-commit-{self.env.new_serialno("pre-commit"):d}'
		targetnode = nodes.section(ids=[targetid])

		yaml_dumper = YAML()
		yaml_dumper.default_flow_style = False

		yaml_output_stream = StringIO()
		yaml_dumper.dump([config], stream=yaml_output_stream)

		yaml_output = yaml_output_stream.getvalue()

		if not yaml_output:
			return []

		content = f".. code-block:: yaml\n\n{indent(yaml_output, '    ')}\n\n"
		view = StringList(content.split('\n'))
		pre_commit_node = nodes.paragraph(rawsource=content)
		self.state.nested_parse(view, self.content_offset, pre_commit_node)

		pre_commit_f8_node_purger.add_node(self.env, pre_commit_node, targetnode, self.lineno)

		return [pre_commit_node]


def revert_8345():
	"""
	Remove the incorrect warning emitted since https://github.com/sphinx-doc/sphinx/pull/8345.
	"""

	#  Copyright (c) 2007-2020 by the Sphinx team (see AUTHORS file).
	#  BSD Licensed
	#  All rights reserved.
	#
	#  Redistribution and use in source and binary forms, with or without
	#  modification, are permitted provided that the following conditions are
	#  met:
	#
	#  * Redistributions of source code must retain the above copyright
	#   notice, this list of conditions and the following disclaimer.
	#
	#  * Redistributions in binary form must reproduce the above copyright
	#   notice, this list of conditions and the following disclaimer in the
	#   documentation and/or other materials provided with the distribution.
	#
	#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
	#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
	#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
	#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
	#  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
	#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
	#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
	#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
	#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
	#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
	#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

	def lookup_domain_element(self, type: str, name: str) -> Any:  # noqa: A002  # pylint: disable=redefined-builtin
		"""
		Lookup a markup element (directive or role), given its name which can be a full name (with domain).
		"""

		name = name.lower()
		# explicit domain given?
		if ':' in name:
			domain_name, name = name.split(':', 1)
			if domain_name in self.env.domains:
				domain = self.env.get_domain(domain_name)
				element = getattr(domain, type)(name)
				if element is not None:
					return element, []
		# else look in the default domain
		else:
			def_domain = self.env.temp_data.get("default_domain")
			if def_domain is not None:
				element = getattr(def_domain, type)(name)
				if element is not None:
					return element, []

		# always look in the std domain
		element = getattr(self.env.get_domain("std"), type)(name)
		if element is not None:
			return element, []

		raise sphinx.util.docutils.ElementLookupError

	sphinx.util.docutils.sphinx_domains.lookup_domain_element = lookup_domain_element  # type: ignore


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.pre_commit`.

	:param app: The Sphinx application.
	"""

	app.add_directive("pre-commit", PreCommitDirective)
	app.add_directive("pre-commit:flake8", Flake8PreCommitDirective)
	app.connect("env-purge-doc", pre_commit_node_purger.purge_nodes)
	app.connect("env-purge-doc", pre_commit_f8_node_purger.purge_nodes)

	if sphinx.version_info >= (4, 0):
		revert_8345()

	return {"parallel_read_safe": True}

#!/usr/bin/env python3
#
#  installation.py
"""
The :rst:dir:`installation` directive.
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
import inspect
import warnings
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple

# 3rd party
import sphinx.environment
from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import ViewList
from sphinx.environment import BuildEnvironment
from sphinx.util.docutils import SphinxDirective

# this package
from sphinx_toolbox.utils import OptionSpec, Purger, flag, word_join

__all__ = [
		"Sources",
		"sources",
		"pypi_installation",
		"conda_installation",
		"github_installation",
		"InstallationDirective",
		"make_installation_instructions",
		"ExtensionsDirective",
		"installation_node_purger",
		"extensions_node_purger",
		]


class Sources(List[Tuple[str, str, Callable, Callable, Optional[Dict[str, Callable]]]]):
	"""
	Class to store functions that provide installation instructions for different sources.

	The syntax of each entry is:

	``(option_name, source_name, getter_function, validator_function, extra_options)``

	* a string to use in the directive to specify the source to use,
	* a string to use in the tabs to indicate the installation source,
	* the function that returns the installation instructions,
	* a function to validate the option value provided by the user,
	* a mapping of additional options for the directive that are used by the getter_function.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	_args = ["options", "env"]
	_directive_name = "installation"

	def register(
			self,
			option_name: str,
			source_name: str,
			validator: Callable = directives.unchanged,
			extra_options: Optional[Dict[str, Callable]] = None,
			) -> Callable:
		"""
		Decorator to register a function.

		The function must have the following signature:

		.. code-block:: python

			def function(
				options: Dict[str, Any],  # Mapping of option names to values.
				env: sphinx.environment.BuildEnvironment,  # The Sphinx build environment.
				) -> List[str]: ...

		:param option_name: A string to use in the directive to specify the source to use.
		:param source_name: A string to use in tabbed installation instructions to represent this source.
		:param validator: A function to validate the option value provided by the user.
		:default validator: :func:`docutils.parsers.rst.directives.unchanged`
		:param extra_options: An optional mapping of extra option names to validator functions.
		:default extra_options: ``{}``

		:return: The registered function.

		:raises: :exc:`SyntaxError` if the decorated function does not take the correct arguments.
		"""

		def _decorator(function: Callable) -> Callable:
			signature = inspect.signature(function)

			if list(signature.parameters.keys()) != self._args:
				raise SyntaxError(  # pragma: no cover
					"The decorated function must take only the following arguments: "
					f"{word_join(self._args, use_repr=True, oxford=True)}"
					)

			self.append((option_name, source_name, function, validator, extra_options or {}))

			setattr(function, f"_{self._directive_name}_registered", True)

			return function

		return _decorator


#: Instance of :class:`~.Sources`.
sources: Sources = Sources()


# pypi_name: The name of the project on PyPI.
@sources.register("pypi", "PyPI", flag, {"pypi-name": directives.unchanged})
def pypi_installation(
		options: Dict[str, Any],
		env: sphinx.environment.BuildEnvironment,
		) -> List[str]:
	"""
	Source to provide instructions for installing from PyPI.

	:param options: Mapping of option names to values.
	:param env: The Sphinx build environment.
	"""

	if "pypi-name" in options:
		pypi_name = options["pypi-name"]
	elif "project_name" in options:
		pypi_name = options["project_name"]
	else:
		raise ValueError("No username supplied for the PyPI installation instructions.")

	return [".. prompt:: bash", '', f"    python3 -m pip install {pypi_name} --user"]


# conda_name: The name of the project on PyPI.
@sources.register(
		"anaconda",
		"Anaconda",
		flag,
		{"conda-name": directives.unchanged, "conda-channels": directives.unchanged},
		)
def conda_installation(
		options: Dict[str, Any],
		env: sphinx.environment.BuildEnvironment,
		) -> List[str]:
	"""
	Source to provide instructions for installing from Anaconda.

	:param options: Mapping of option names to values.
	:param env: The Sphinx build environment.
	"""

	if "conda-name" in options:
		conda_name = options["conda-name"]
	elif "pypi-name" in options:
		conda_name = options["pypi-name"]
	elif "project_name" in options:
		conda_name = options["project_name"]
	else:
		raise ValueError("No username supplied for the Anaconda installation instructions.")

	lines = []

	if "conda-channels" in options:
		channels = str(options["conda-channels"]).split(",")
	else:
		channels = env.config.conda_channels

	if channels:
		lines.extend([
				"First add the required channels",
				'',
				".. prompt:: bash",
				'',
				])

		for channel in channels:
			lines.append(f"    conda config --add channels https://conda.anaconda.org/{channel.strip()}")

		lines.extend(['', "Then install"])

	if lines:
		lines.append('')

	lines.extend([".. prompt:: bash", '', f"    conda install {conda_name}"])

	return lines


@sources.register("github", "GitHub", flag)
def github_installation(
		options: Dict[str, Any],
		env: sphinx.environment.BuildEnvironment,
		) -> List[str]:
	"""
	Source to provide instructions for installing from GitHub.

	:param options: Mapping of option names to values.
	:param env: The Sphinx build environment.
	"""

	username = env.config.github_username  # type: ignore
	repository = env.config.github_repository  # type: ignore

	return [
			".. prompt:: bash",
			'',
			f"    python3 -m pip install git+https://github.com/{username}/{repository}@master --user"
			]


class InstallationDirective(SphinxDirective):
	"""
	Directive to show installation instructions.
	"""

	has_content: bool = True
	optional_arguments: int = 1  # The name of the project; can be overridden for each source

	# Registered sources
	option_spec: OptionSpec = {  # type: ignore
		source[0].lower(): source[3]
		for source in sources  # pylint: disable=not-an-iterable
		}

	# Extra options for registered sources
	for source in sources:  # pylint: disable=not-an-iterable
		if source[4] is not None:
			option_spec.update(source[4])  # type: ignore

	options: Dict[str, Any]
	"""
	Mapping of option names to values.

	The options are as follows:

	* **pypi**: Flag to indicate the project can be installed from PyPI.
	* **pypi-name**: The name of the project on PyPI.
	* **conda**: Flag to indicate the project can be installed with Conda.
	* **conda-name**: The name of the project on Conda.
	* **conda-channels**: Comma-separated list of required Conda channels.
	* **github**:  Flag to indicate the project can be installed from GitHub.

	The GitHub username and repository are configured in ``conf.py`` and are available in ``env.config``.
	"""

	def run(self) -> List[nodes.Node]:
		"""
		Create the installation node.

		:return:
		"""

		if self.arguments:
			self.options["project_name"] = self.arguments[0]

		targetid = f'installation-{self.env.new_serialno("sphinx-toolbox installation"):d}'
		targetnode = nodes.target('', '', ids=[targetid])

		content = make_installation_instructions(self.options, self.env)
		view = ViewList(content)

		installation_node = nodes.paragraph(rawsource=content)  # type: ignore
		self.state.nested_parse(view, self.content_offset, installation_node)  # type: ignore
		installation_node_purger.add_node(self.env, installation_node, targetnode, self.lineno)

		return [targetnode, installation_node]


def make_installation_instructions(options: Dict[str, Any], env: BuildEnvironment) -> List[str]:
	"""
	Make the content of an installation node.

	:param options:
	:param env:

	:return:
	"""

	tabs: Dict[str, List[str]] = {}

	for option_name, source_name, getter_function, validator_function, extra_options in sources:
		if option_name in options:
			tabs[f"from {source_name}"] = getter_function(options, env)

	if tabs:
		content = [".. tabs::", '']

		for tab_name, tab_content in tabs.items():
			content.extend([f"    .. tab:: {tab_name}", ''])
			content.extend([f"        {line}" if line else '' for line in tab_content])

		return content

	else:
		warnings.warn("No installation source specified. No installation instructions will be shown.")
		return []


class ExtensionsDirective(SphinxDirective):
	"""
	Directive to show instructions for enabling the extension.
	"""

	has_content: bool = True  # Other required extensions, one per line
	optional_arguments: int = 1  # The name of the project
	option_spec: OptionSpec = {  # type: ignore
		"import-name": directives.unchanged_required,  # If different to project name
		"no-preamble": flag,
		"no-postamble": flag,
		"first": flag,
		}

	def run(self) -> List[nodes.Node]:
		"""
		Create the extensions node.

		:return:
		"""

		extensions = list(self.content)
		first = self.options.get("first", False)

		if "import-name" in self.options and first:
			extensions.insert(0, self.options["import-name"])
		elif "import-name" in self.options:
			extensions.append(self.options["import-name"])
		elif first:
			extensions.insert(0, self.arguments[0])
		else:
			extensions.append(self.arguments[0])

		targetid = f'extensions-{self.env.new_serialno("sphinx-toolbox extensions"):d}'
		targetnode = nodes.target('', '', ids=[targetid])

		top_text = (
				f"Enable ``{self.arguments[0]}`` by adding the following "
				f"to the ``extensions`` variable in your ``conf.py``:"
				)
		bottom_text = (
				"For more information see "
				"https://www.sphinx-doc.org/en/master/usage/extensions/index.html#third-party-extensions ."
				)

		if "no-preamble" in self.options:
			content = []
		else:
			content = [top_text, '']

		content.extend([
				".. code-block:: python",
				'',
				"    extensions = [",
				"        ...",
				])

		for extension in extensions:
			content.append(f"        {extension!r},")

		content.extend(["        ]", ''])

		if "no-postamble" not in self.options:
			content.extend([bottom_text, ''])

		view = ViewList(content)

		extensions_node = nodes.paragraph(rawsource=content)  # type: ignore
		self.state.nested_parse(view, self.content_offset, extensions_node)  # type: ignore
		extensions_node_purger.add_node(self.env, extensions_node, targetnode, self.lineno)

		return [targetnode, extensions_node]


installation_node_purger = Purger("all_installation_node_nodes")
extensions_node_purger = Purger("all_extensions_node_nodes")

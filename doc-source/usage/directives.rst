=============
Directives
=============

.. rst:directive:: code-block

	Customised ``.. code-block::`` directive with an adjustable indent size.

	.. rst:directive:option:: tab-width: number
		:type: number

		Sets the size of the indentation in spaces.


	All other options from :rst:dir:`sphinx:code-block` are available,
	see the `Sphinx documentation <https://www.sphinx-doc.org/en/3.x/usage/restructuredtext/directives.html#directive-code-block>`_ for details.

	**Examples**

	.. rest-example::

		.. code-block:: python

			def print(text):
				sys.stdout.write(text)


	.. rest-example::

		.. code-block:: python
			:tab-width: 8

			def print(text):
				sys.stdout.write(text)



.. rst:directive:: confval

	Used to document a configuration value.

	.. rst:directive:option:: type
		:type: string

		Indicates the configuration value's type.

	.. rst:directive:option:: required
		:type: flag

		Indicates the whether the configuration value is required.

	.. rst:directive:option:: default
		:type: string

		Indicates the default value.

.. rst:directive:: extensions

	Shows instructions on how to enable a Sphinx extension.

	Takes a single argument -- the name of the extension.

	.. rst:directive:option:: import-name
		:type: string

		The name used to import the extension, if different from the name of the extension.

	.. rst:directive:option:: no-preamble
		:type: flag

		Disables the preamble text.

	.. rst:directive:option:: no-postamble
		:type: flag

		Disables the postamble text.

	.. rst:directive:option:: first
		:type: flag

		Puts the entry for extension before its dependencies.
		By default is is placed at the end.

		.. versionadded:: 0.4.0


	**Example**

	.. rest-example::

		.. extensions:: sphinx-toolbox
			:import-name: sphinx_toolbox

			sphinx.ext.viewcode
			sphinx_tabs.tabs
			sphinx-prompt


.. rst:directive:: installation

	Adds a series of tabs providing installation instructions for the project from a number of sources.

	The directive has a single required argument -- the name of the project.
	If the project uses a different name on PyPI and/or Anaconda, the ``pypi-name`` and ``conda-name`` options can be used to set the name for those repositories.

	.. rst:directive:option:: pypi
		:type: flag

		Flag to indicate the project can be installed from PyPI.

	.. rst:directive:option:: pypi-name: name
		:type: string

		The name of the project on PyPI.

	.. rst:directive:option:: conda
		:type: flag

		Flag to indicate the project can be installed with Conda.

	.. rst:directive:option:: conda-name: name
		:type: string

		The name of the project on Conda.

	.. rst:directive:option:: conda-channels: line numbers
		:type: comma separated numbers

		Comma-separated list of required Conda channels.

	.. rst:directive:option:: github
		:type: flag

		Flag to indicate the project can be installed from GitHub.


	The GitHub username and repository are configured in ``conf.py`` (see :ref:`Configuration`)


	**Example**

	.. rest-example::

		.. installation:: sphinx-toolbox
			:pypi:
			:anaconda:
			:conda-channels: domdfcoding,conda-forge
			:github:


.. rst:directive:: rest-example

	Directive to show example reStructuredText and the rendered output.

	.. rst:directive:option:: force
		:type: flag

		If given, minor errors on highlighting are ignored.

	.. rst:directive:option:: emphasize-lines: line numbers
		:type: comma separated numbers

		Emphasize particular lines of the code block:

	.. rst:directive:option:: tab-width: number
		:type: number

		Sets the size of the indentation in spaces.

	.. rst:directive:option:: dedent: number
		:type: number

		Strip indentation characters from the code block,


	**Example**

	.. rest-example::

		.. rest-example::

			:source:`sphinx_toolbox/config.py`

			Here is the :source:`source code <sphinx_toolbox/config.py>`


.. rst:directive:: autoprotocol

	Directive to automatically document a :class:`typing.Protocol`.

	The output is based on the :rst:dir:`autoclass` directive, but with a few differences:

	* Private members are always excluded.
	* Special members (dunder methods) are always included.
	* Undocumented members are always included.

	The following options from :rst:dir:`autoclass` are available:

	.. rst:directive:option:: noindex
		:type: flag

		Do not generate index entries for the documented object (and all autodocumented members).

	.. rst:directive:option:: member-order
		:type: string

		Override the global value of ``autodoc_member_order`` for one directive.

	See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
	for further information.

	**Examples:**

	.. rest-example::

		.. automodule:: autoprotocol_demo
			:members:
			:no-autosummary:
			:exclude-members: HasGreaterThan

		.. autoprotocol:: autoprotocol_demo.HasGreaterThan


.. rst:directive:: autotypeddict

	Directive to automatically document a :class:`typing.TypedDict`.

	The output is based on the :rst:dir:`autoclass` directive, but with a few differences:

	* Private and Special members are always excluded.
	* Undocumented members are always included.
	* The default sort order is ``bysource``.

	The following options are available:

	.. rst:directive:option:: noindex
		:type: flag

		Do not generate index entries for the documented object (and all autodocumented members).

	.. rst:directive:option:: alphabetical
		:type: flag

		Sort the keys alphabetically. By default the keys are listed in the order they were defined.

	See https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
	for further information.

	**Examples:**

	.. rest-example::

		.. automodule:: autotypeddict_demo
			:no-autosummary:
			:exclude-members: Movie

		.. autotypeddict:: autotypeddict_demo.Movie

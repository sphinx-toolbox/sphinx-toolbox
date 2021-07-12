============
Overview
============

.. py:module:: sphinx_toolbox

.. extensions:: sphinx-toolbox
	:import-name: sphinx_toolbox
	:no-postamble:

	sphinx.ext.viewcode
	sphinx_tabs.tabs
	sphinx-prompt


The following features are enabled by default:

* :mod:`sphinx_toolbox.assets`
* :mod:`sphinx_toolbox.changeset`
* :mod:`sphinx_toolbox.code`
* :mod:`sphinx_toolbox.collapse`
* :mod:`sphinx_toolbox.confval`
* :mod:`sphinx_toolbox.decorators`
* :mod:`sphinx_toolbox.formatting`
* :mod:`sphinx_toolbox.github`
* :mod:`sphinx_toolbox.installation`
* :mod:`sphinx_toolbox.issues`
* :mod:`sphinx_toolbox.latex`
* :mod:`sphinx_toolbox.rest_example`
* :mod:`sphinx_toolbox.shields` *
* :mod:`sphinx_toolbox.sidebar_links`
* :mod:`sphinx_toolbox.source`
* :mod:`sphinx_toolbox.wikipedia`
* :mod:`sphinx_toolbox.more_autodoc.autonamedtuple`
* :mod:`sphinx_toolbox.more_autodoc.autoprotocol`
* :mod:`sphinx_toolbox.more_autodoc.autotypeddict`


\* Indicates that the extension cannot be enabled separately from the rest of ``sphinx_toolbox``.

.. clearpage::

Some features must be enabled separately:

* :mod:`sphinx_toolbox.documentation_summary`

	Allows insertion of a summary line on the title page generated with the LaTeX builder.

* :mod:`sphinx_toolbox.flake8`

	Provides a directive for creating a table of Flake8 codes.

	.. note:: Requires the ``flake8`` extra to be installed (``pip install sphinx-toolbox[flake8]``)

* :mod:`sphinx_toolbox.pre_commit`

	Provides directives to show examples of ``.pre-commit-config.yaml`` configuration.

	.. note:: Requires the ``precommit`` extra to be installed (``pip install sphinx-toolbox[precommit]``)

* :mod:`sphinx_toolbox.more_autodoc`

	* :mod:`sphinx_toolbox.more_autodoc.augment_defaults`
	* :mod:`sphinx_toolbox.more_autodoc.generic_bases`
	* :mod:`sphinx_toolbox.more_autodoc.genericalias`
	* :mod:`sphinx_toolbox.more_autodoc.no_docstring`
	* :mod:`sphinx_toolbox.more_autodoc.overloads`
	* :mod:`sphinx_toolbox.more_autodoc.regex`
	* :mod:`sphinx_toolbox.more_autodoc.sourcelink`
	* :mod:`sphinx_toolbox.more_autodoc.typehints`
	* :mod:`sphinx_toolbox.more_autodoc.typevars`
	* :mod:`sphinx_toolbox.more_autodoc.variables`

	:mod:`sphinx_toolbox.more_autodoc` can also be specified as an extension, which enables all of the above features.

* :mod:`sphinx_toolbox.more_autosummary`

	Provides a patched version of :class:`sphinx.ext.autosummary.Autosummary`
	to fix an issue where the module name is sometimes duplicated.

	I.e. ``foo.bar.baz()`` became ``foo.bar.foo.bar.baz()``, which of course doesn't exist
	and created a broken link.

* :mod:`sphinx_toolbox.tweaks.* <sphinx_toolbox.tweaks>`

	Provides various tweaks to Sphinx's output.

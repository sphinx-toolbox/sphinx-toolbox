============
Overview
============


.. extensions:: sphinx-toolbox
	:import-name: sphinx_toolbox
	:no-postamble:

	sphinx.ext.viewcode
	sphinx_tabs.tabs
	sphinx-prompt


The following features are enabled by default:

* :mod:`sphinx_toolbox.assets`
* :mod:`sphinx_toolbox.code`
* :mod:`sphinx_toolbox.confval`
* :mod:`sphinx_toolbox.decorators`
* :mod:`sphinx_toolbox.formatting`
* :mod:`sphinx_toolbox.installation`
* :mod:`sphinx_toolbox.issues`
* :mod:`sphinx_toolbox.rest_example`
* :mod:`sphinx_toolbox.shields` *
* :mod:`sphinx_toolbox.source`
* :mod:`sphinx_toolbox.wikipedia`
* :mod:`sphinx_toolbox.more_autodoc.autonamedtuple`
* :mod:`sphinx_toolbox.more_autodoc.autoprotocol`
* :mod:`sphinx_toolbox.more_autodoc.autotypeddict`


\* Indicates that the extension cannot be enabled separately from the rest of ``sphinx_toolbox``.


Some features must be enabled separately:

* :mod:`sphinx_toolbox.more_autodoc`

	* :mod:`sphinx_toolbox.more_autodoc.augment_defaults`
	* :mod:`sphinx_toolbox.more_autodoc.genericalias`
	* :mod:`sphinx_toolbox.more_autodoc.no_docstring`
	* :mod:`sphinx_toolbox.more_autodoc.sourcelink`
	* :mod:`sphinx_toolbox.more_autodoc.typehints`
	* :mod:`sphinx_toolbox.more_autodoc.variables`

	:mod:`sphinx_toolbox.more_autodoc` can also be specified as an extension, which enables all of the above features.

* :mod:`sphinx_toolbox.more_autosummary`

	Provides a patched version of :class:`sphinx.ext.autosummary.Autosummary`
	to fix an issue where the module name is sometimes duplicated.

	I.e. ``foo.bar.baz()`` became ``foo.bar.foo.bar.baz()``, which of course doesn't exist
	and so resulted in a broken link.

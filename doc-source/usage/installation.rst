==============
Installation
==============

.. installation:: sphinx-toolbox
	:pypi:
	:github:


.. extensions:: sphinx-toolbox
	:import-name: sphinx_toolbox
	:no-postamble:

	sphinx.ext.viewcode
	sphinx_tabs.tabs
	sphinx-prompt

There is also the ``sphinx_toolbox.autodoc_augment_defaults`` extension that has additional requirements
and must be enabled separately:

.. extensions:: sphinx_toolbox.autodoc_augment_defaults
	:no-preamble:

	sphinx.ext.autodoc

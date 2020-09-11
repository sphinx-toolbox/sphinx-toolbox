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

Some features of this extension must be enabled separately:

* ``sphinx_toolbox.autodoc_augment_defaults`` allows for default options to be specified in
  `autodoc_default_options <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options>`_
  and then extend those option in each autodoc directive.

  .. extensions:: sphinx_toolbox.autodoc_augment_defaults
      :no-preamble:
      :no-postamble:
      :first:

      sphinx.ext.autodoc

* ``sphinx_toolbox.autodoc_typehints``. An enhanced version of
  `sphinx-autodoc-typehints <https://pypi.org/project/sphinx-autodoc-typehints/>`_.

  .. extensions:: sphinx_toolbox.autodoc_typehints
      :no-preamble:
      :no-postamble:
      :first:

      sphinx.ext.autodoc
      sphinx_autodoc_typehints

For more information see https://www.sphinx-doc.org/en/master/usage/extensions/index.html#third-party-extensions .

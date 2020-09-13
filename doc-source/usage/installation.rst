==============
Installation
==============

.. installation:: sphinx-toolbox
	:pypi:
	:github:
	:anaconda:
	:conda-channels: domdfcoding,conda-forge


.. extensions:: sphinx-toolbox
	:import-name: sphinx_toolbox
	:no-postamble:

	sphinx.ext.viewcode
	sphinx_tabs.tabs
	sphinx-prompt

Some features of this extension must be enabled separately:

* ``sphinx_toolbox.more_autodoc.augment_defaults`` allows for default options to be specified in
  `autodoc_default_options <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#confval-autodoc_default_options>`_
  and then extend those option in each autodoc directive.

  .. extensions:: sphinx_toolbox.more_autodoc.augment_defaults
      :no-preamble:
      :no-postamble:
      :first:

      sphinx.ext.autodoc

* ``sphinx_toolbox.more_autodoc.typehints``: An enhanced version of
  `sphinx-autodoc-typehints <https://pypi.org/project/sphinx-autodoc-typehints/>`_.

  .. extensions:: sphinx_toolbox.more_autodoc.typehints
      :no-preamble:
      :no-postamble:
      :first:

      sphinx.ext.autodoc
      sphinx_autodoc_typehints

* ``sphinx_toolbox.more_autodoc.genericalias``: An enhanced version of autodoc's generic alias with
  links to the aliased objects.

  .. extensions:: sphinx_toolbox.more_autodoc.genericalias
      :no-preamble:
      :no-postamble:
      :first:

      sphinx.ext.autodoc

* ``sphinx_toolbox.patched_autosummary``: A patched version of :class:`sphinx.ext.autosummary.Autosummary`
  to fix an issue where the module name is sometimes duplicated.

  I.e. ``foo.bar.baz()`` became ``foo.bar.foo.bar.baz()``, which of course doesn't exist
  and so resulted in a broken link.

  .. extensions:: sphinx_toolbox.patched_autosummary
      :no-preamble:
      :no-postamble:

      sphinx.ext.autosummary

|

For more information see https://www.sphinx-doc.org/en/master/usage/extensions/index.html#third-party-extensions .

.. TODO:: sourcelink and variables

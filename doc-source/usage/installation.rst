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

* ``sphinx_toolbox.more_autodoc``: Extends autodoc with support for
  :class:`Protocols <typing.Protocol>`,
  :class:`TypedDicts <typing.TypedDict>`,
  :pep:`484` type hints,
  module and class summary tables, and more.

  .. extensions:: sphinx_toolbox.more_autodoc
      :no-preamble:
      :no-postamble:
      :first:

* ``sphinx_toolbox.more_autosummary``: A patched version of :class:`sphinx.ext.autosummary.Autosummary`
  to fix an issue where the module name is sometimes duplicated.

  I.e. ``foo.bar.baz()`` became ``foo.bar.foo.bar.baz()``, which of course doesn't exist
  and so resulted in a broken link.

  .. extensions:: sphinx_toolbox.more_autosummary
      :no-preamble:
      :no-postamble:

      sphinx.ext.autosummary

|

For more information see https://www.sphinx-doc.org/en/master/usage/extensions/index.html#third-party-extensions .

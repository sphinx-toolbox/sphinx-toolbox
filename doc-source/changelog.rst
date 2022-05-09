===============
Changelog
===============


3.0.0 (Unreleased)
----------------------

Additions
^^^^^^^^^^^

* Official support for Sphinx 4.5 and docutils 0.17
* :mod:`sphinx_toolbox.collapse` -- Added the ``:open:`` option for having the collapsable section open by default. Suggested by :github:user:`tdegeus` in :github:issue:`96`. (PR :github:pull:`101`)
* :mod:`sphinx_toolbox.more_autosummary.column_widths` -- Allows for the autosummary table column widths to be customised with the LaTeX builder. (PR :github:pull:`100`)
* :mod:`sphinx_toolbox.tweaks.latex_layout` -- Added the :confval:`needspace_amount` option for configuring the LaTeX ``needspace`` extension.
* Add :mod:`sphinx_toolbox.latex.succinct_seealso` and make :mod:`sphinx_toolbox.latex` a package.

Moves
^^^^^^^^^^

* :mod:`sphinx_toolbox.tweaks.latex_layout` -- Moved to :mod:`sphinx_toolbox.latex.layout`.
* :mod:`sphinx_toolbox.tweaks.latex_toc` -- Moved to :mod:`sphinx_toolbox.latex.toc`.

Removals
^^^^^^^^

* Python 3.6 (including CPython 3.6 and PyPy 3.6) are no longer supported. (PR :github:pull:`99`)
* :mod:`sphinx_toolbox.issues` -- ``IssueNode``, ``visit_issue_node``, ``depart_issue_node``, ``get_issue_title``. Import from :mod:`sphinx_toolbox.github.issues` instead.
* ``sphinx_toolbox.tweaks.sphinx_panels_tabs.copy_assets`` -- renamed to :func:`~sphinx_toolbox.tweaks.sphinx_panels_tabs.copy_asset_files`.
* ``sphinx_toolbox.utils.begin_generate``

Bugs Fixed
^^^^^^^^^^^

* :mod:`sphinx_toolbox.more_autodoc.overloads` -- Now try to resolve forward references in function overloads.
* :mod:`sphinx_toolbox.confval` -- :rst:dir:`confval` directives now show up in the index.
* :rst:dir:`autonamedtuple`, :rst:dir:`autoprotocol`, :rst:dir:`autotypeddict` -- Index entries are now created. (PR :github:pull:`103`)

2.18.2
--------------

Bugs Fixed
^^^^^^^^^^^

* :mod:`sphinx_toolbox.github` now correctly parses issue titles containing code and quote characters. Reported by :github:user:`arisp99` in :github:issue:`91`.
* :mod:`sphinx_toolbox.more_autosummary` -- Restore compatibility with latest autodocsumm. For the time being autodocsumm's ``relative_ref_paths`` option is not supported.


2.18.0
--------------

``consolekit`` is no longer a dependency;
:class:`~.TerminalRegexParser` now contains the necessary code to create coloured text itself.


2.17.0
--------------

Additions
^^^^^^^^^^^

* :func:`sphinx_toolbox.testing.latex_regression` and :class:`sphinx_toolbox.testing.LaTeXRegressionFixture`
* The ``jinja2_namespace`` argument to :class:`sphinx_toolbox.testing.HTMLRegressionFixture.check`


Bugs Fixed
^^^^^^^^^^^

* Close the underlying requests session of :data:`sphinx_toolbox.utils.GITHUB_COM` when the Python interpreter exits.
* :func:`sphinx_toolbox.more_autodoc.typehints.process_docstring` is skipped for ``variable`` and ``regex`` documenters
  where there aren't ``:param:`` and ``:rtype:`` attributes.


2.16.1
--------------

Removed top-end requirement for Sphinx.
The officially supported versions are Sphinx 3.2 to 4.4 inclusive.


2.16.0
--------------

Bugs Fixed
^^^^^^^^^^^^

* :mod:`sphinx_toolbox.more_autodoc` -- Ensure the ``|nbsp|`` substitution is set up correctly when the ``rst_prolog`` option is specified in ``conf.py`` (Issue :issue:`80`).
  when using the extension on its own.
* Set the ``class`` CSS class with custom autodocumenters (:mod:`~.autonamedtuple`, :mod:`~.autoprotocol` and :mod:`~.autotypeddict`) (Issue :issue:`79`)


Additions
^^^^^^^^^^^

* :func:`sphinx_toolbox.utils.add_fallback_css_class`
* :class:`sphinx_toolbox.testing.HTMLRegressionFixture` -- made the ``docutils_version`` variable available in jinja2 templates.

2.15.3
--------------

Features
^^^^^^^^^^^

* Support ``sphinx-autodoc-typehints`` versions 1.12-1.14.


Bugs Fixed
^^^^^^^^^^^^

* :mod:`sphinx_toolbox.more_autodoc.regex` -- Ensure the ``|nbsp|`` substitution is set up
  when using the extension on its own (Issue :issue:`80`).


Deprecations
^^^^^^^^^^^^^^

* ``sphinx_toolbox.utils.begin_generate`` -- Will be removed in v3.0.0.
  Users of this function should reimplement it in their own code.

2.15.2
--------------

Bugs Fixed
^^^^^^^^^^^^

* :mod:`sphinx_toolbox.decorators` -- Ensure the ``deco`` role correctly finds the targets of xrefs.

2.15.1
------------

Bugs Fixed
^^^^^^^^^^^^^

* :mod:`sphinx_toolbox.github` -- fix crash when getting GitHub issue titles if there's no internet.

2.15.0
------------

Features
^^^^^^^^^

* Added support for Sphinx 4.1 and 4.2
* Added support for autodocsumm > 0.2.2
* Improved support for Python 3.10.0 rc.2

Bugs Fixed
^^^^^^^^^^^^^

* :class:`~.RegexDocumenter` -- No longer outputs a ``csv-table`` directive when there is no pattern and no flags. This prevents docutils emitting a warning.
* Correctly uses UTF-8 when reading files in HTML regression tests.

2.14.0
--------

Features
^^^^^^^^^

* :class:`sphinx_toolbox.testing.HTMLRegressionFixture` -- Added support for rendering the reference file as a jinja2 template, which can be used to account for differences between Python and Sphinx versions.
* Added support for Sphinx 4.0 and sphinx-tabs versions up to 3.2.0
* Improved support for Python 3.10.0 rc.1
* :mod:`sphinx_toolbox.tweaks.latex_layout` -- Now configures ``hyperref`` to use correct page numbering for the frontmatter.

Bugs Fixed
^^^^^^^^^^^^^

* URLs pointing to https://pypistats.org/ now use lowercased project names.
* The ``cls`` and ``return`` attributes are ignored from ``__annotations__`` when deciding whether to include the ``__new__`` method for a :class:`~.NamedTuple` with :class:`~.NamedTupleDocumenter`.


2.13.0
--------

Features
^^^^^^^^^^

* Added support for Sphinx 3.4.x and 3.5.x.
* :mod:`sphinx_toolbox.more_autodoc.autoprotocol` -- Added support for generic bases, such as ``class SupportsAbs(Protocol[T_co]): ...``.
* :mod:`sphinx_toolbox.more_autosummary` -- Added the :confval:`autosummary_col_type` configuration option.
* :func:`sphinx_toolbox.latex.replace_unknown_unicode` -- Add support for converting ``≥`` and ``≤``.
* :func:`sphinx_toolbox.more_autodoc.typehints.format_annotation` -- Added support for :py:obj:`True` and :py:obj:`False`

Bugs Fixed
^^^^^^^^^^^^^

* :mod:`sphinx_toolbox.more_autosummary` -- Ensure ``__all__`` is respected for autosummary tables.


-----

.. note:: The changlog prior to 2.13.0 has not been compiled yet.

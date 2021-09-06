===============
Changelog
===============

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

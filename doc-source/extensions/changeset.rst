=================================
:mod:`~sphinx_toolbox.changeset`
=================================

.. automodule:: sphinx_toolbox.changeset
	:member-order: bysource
	:no-autosummary:
	:exclude-members: run


Examples
---------------

.. rest-example::

	.. versionadded:: 2.4
	.. versionadded:: 2.5  The *spam* parameter.

	.. versionadded:: 2.6
		The *parrot* parameter.

.. rest-example::

	.. deprecated:: 3.1
		Use :func:`spam` instead.

	.. deprecated:: 3.2  Use :func:`lobster` instead.

.. rest-example::

	.. versionremoved:: 1.2.3  Use :func:`foo` instead.

	.. versionremoved:: 1.2.3

		Due to an unfixable bug this function has been removed.
		If you desperately need this functionality please write to the mailing list at
		:email:`python-users@example.org`

.. only:: html

	.. rest-example::

		.. versionchanged:: 0.3.0

			* Parameters for ``__init__`` can be documented either in the class docstring
			  or alongside the attribute.
			  The class docstring has priority.
			* Added support for `autodocsumm <https://github.com/Chilipp/autodocsumm>`_.

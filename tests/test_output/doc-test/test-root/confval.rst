:orphan:

=========
Confval
=========

.. confval:: source_link_target
	:type: :class:`str`
	:required: False
	:default: ``'Sphinx'``

	The target of the source link, either ``'GitHub'`` or ``'Sphinx'``.
	Case insensitive.

.. confval:: github_username
	:type: :class:`str`
	:required: True


.. confval:: github_repository
	:type: :class:`str`
	:required: True

	The GitHub repository this documentation corresponds to.

.. confval:: conda_channels
	:type: Comma-separated list of strings
	:required: True

	The conda channels required to install the library from Anaconda.


.. confval:: github_repository
	:type: :class:`str`
	:noindex:

	This is a duplicate with ``:noindex:`` set.

This is an xref to the :confval:`github_repository` configuration option.


.. confval:: something

	A configuration value.

==============
Configuration
==============

.. confval:: source_link_target
	:type: :class:`str`
	:required: False
	:default: ``'Sphinx'``

	The target of the source link, either ``'GitHub'`` or ``'Sphinx'``.
	Case insensitive.

.. confval:: github_username
	:type: :class:`str`
	:required: True

	The username of the GitHub account that owns the repository this documentation corresponds to.

.. confval:: github_repository
	:type: :class:`str`
	:required: True

	The GitHub repository this documentation corresponds to.

.. confval:: conda_channels
	:type: :class:`~typing.List`\[:class:`str`\]
	:required: False
	:default: ``[]``

	The conda channels required to install the library from Anaconda.
	An alternative to setting it within the :rst:dir:`installation` directive.

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

.. confval:: wikipedia_lang
	:type: :class:`str`
	:required: False
	:default: ``'en'``

	The Wikipedia language to use for :rst:role:`wikipedia` roles.

	.. versionadded:: 0.2.0

.. confval:: assets_dir
	:type: :class:`str`
	:required: False
	:default: ``'./assets'``

	The directory in which to find assets for the :rst:role:`asset` role.

	.. versionadded:: 0.5.0

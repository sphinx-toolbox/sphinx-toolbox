========
Roles
========

.. rst:role:: source

	Shows a link to the given source file, either on GitHub or within the Sphinx documentation.

	By default the link points to the code within the documentation,
	but can be configured to point to GitHub by setting :confval:`source_link_target` to ``'GitHub'``.

	**Example**

	.. rest-example::

		:source:`sphinx_toolbox/config.py`

		Here is the :source:`source code <sphinx_toolbox/config.py>`


.. rst:role:: issue

	Shows a link to the given issue on GitHub.

	If the issue exists, the link has a tooltip that shows the title of the issue.

	You can also reference an issue in a different repository by adding the repository name inside ``<>``.
	You'll probably want to add some text to tell the user that this issue is from a different project.

	**Example**

	.. rest-example::

		:issue:`1`

		pytest issue :issue:`7680 <pytest-dev/pytest>`


.. rst:role:: pull

	Shows a link to the given pull request on GitHub.

	If the pull requests exists, the link has a tooltip that shows the title of the pull requests.

	You can also reference a pull request in a different repository by adding the repository name inside ``<>``.
	You'll probably want to add some text to tell the user that this pull request is from a different project.

	**Example**

	.. rest-example::

		:pull:`2`

		pytest pull request :issue:`7671 <pytest-dev/pytest>`


The only difference between the :rst:role:`issue` and :rst:role:`pull` roles
is in the URL. GitHub uses the same numbering scheme for issues and
pull requests, and automatically redirects to the pull request if
the user tries to navigate to an issue with that same number.


.. rst:role:: confval

	Shows a link cross-reference to a :rst:dir:`confval`.


.. rst:role:: wikipedia

	Shows a link to the given article on Wikipedia.

	The title and language can be customised.

	.. versionadded:: 0.2.0

	**Example**

	.. rest-example::

		:wikipedia:`Sphinx`

		:wikipedia:`mythical creature <Sphinx>`

		:wikipedia:`:zh:斯芬克斯`

		:wikipedia:`Answer to the Ultimate Question of Life, the Universe, and Everything <:de:42 (Antwort)>`


.. rst:role:: iabbr

	An abbreviation. If the role content contains a parenthesized  explanation,
	it will be treated specially: it will be shown in a tool-tip in HTML,
	and output only once in LaTeX.

	Unlike Sphinx's :rst:role:`abbr` role, this one shows the abbreviation in italics.

	.. versionadded:: 0.2.0

	**Example**

	.. rest-example::

		:iabbr:`LIFO (last-in, first-out)`

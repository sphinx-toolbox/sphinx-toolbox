========
Usage
========

Configuration
--------------

.. confval:: source_link_target

    | **Type:** :class:`str`
    | **Required:** ``False``
    | **Default:** ``'Sphinx'``

    The target of the source link, either ``'GitHub'`` or ``'Sphinx'``.
    Case insensitive.

.. confval:: github_username

    | **Type:** :class:`str`
    | **Required:** ``True``

    The username of the GitHub account that owns the repository this documentation corresponds to.

.. confval:: github_repository

    | **Type:** :class:`str`
    | **Required:** ``True``

    The GitHub repository this documentation corresponds to.

Roles
-----------------

.. rst:role:: source

    Shows a link to the given source file, either on GitHub or within the Sphinx documentation.

    By default the link points to the code within the documentation,
    but can be configured to point to GitHub by setting :confval:`source_link_target` to ``'GitHub'``.

    **Example**

    .. code-block:: rest

        :source:`sphinx_toolbox/config.py`

    :source:`sphinx_toolbox/config.py`


.. rst:role:: issue

    Shows a link to the given issue on GitHub.

    If the issue exists, the link has a tooltip that shows the title of the issue.

    You can also reference an issue in a different repository by adding the repository name inside ``<>``.
    You'll probably want to add some text to tell the user that this issue is from a different project.

    **Example**

    .. code-block:: rest

        :issue:`1`

        pytest issue :issue:`7680 <pytest-dev/pytest>`

    :issue:`1`

    pytest issue :issue:`7680 <pytest-dev/pytest>`


.. rst:role:: pull

    Shows a link to the given pull request on GitHub.

    If the pull requests exists, the link has a tooltip that shows the title of the pull requests.

    You can also reference a pull request in a different repository by adding the repository name inside ``<>``.
    You'll probably want to add some text to tell the user that this pull request is from a different project.

    **Example**

    .. code-block:: rest

        :pull:`2`

        pytest pull request :issue:`7671 <pytest-dev/pytest>`


    :pull:`2`

    pytest pull request :issue:`7671 <pytest-dev/pytest>`


The only difference between the :rst:role:`issue` and :rst:role:`pull` roles
is in the URL. GitHub using the same numbering scheme for issues and
pull requests, and automatically redirects to the pull request if
the user tries to navigate to an issue with that same number.

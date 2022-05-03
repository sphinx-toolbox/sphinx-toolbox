#!/usr/bin/env python3
#
#  issues.py
r"""
Add links to GitHub issues and Pull Requests.

.. extensions:: sphinx_toolbox.issues


Usage
------

.. rst:role:: issue

	Role which shows a link to the given issue on GitHub.

	If the issue exists, the link has a tooltip that shows the title of the issue.

	**Example**

	.. rest-example::

		:issue:`1`

	You can also reference an issue in a different repository by adding the repository name inside ``<>``.

	.. rest-example::

		:issue:`7680 <pytest-dev/pytest>`


.. rst:role:: pull

	Role which shows a link to the given pull request on GitHub.

	If the pull requests exists, the link has a tooltip that shows the title of the pull requests.

	**Example**

	.. rest-example::

		:pull:`2`

	You can also reference a pull request in a different repository by adding the repository name inside ``<>``.

	.. rest-example::

		:pull:`7671 <pytest-dev/pytest>`


.. versionchanged:: 2.4.0

	:rst:role:`issue` and :rst:role:`pull` now show the repository name
	when the name differs from that configured in ``conf.py``.

.. versionchanged:: 2.4.0

	These directives are also available in the :mod:`~.sphinx_toolbox.github` domain.

The only difference between the :rst:role:`issue` and :rst:role:`pull` roles
is in the URL. GitHub uses the same numbering scheme for issues and
pull requests, and automatically redirects to the pull request if
the user tries to navigate to an issue with that same number.


Caching
-----------

HTTP requests to obtain issue/pull request titles are cached for four hours.

To clear the cache manually, run:

.. prompt:: bash

	python3 -m sphinx_toolbox


API Reference
---------------

.. versionchanged:: 2.4.0

	The following moved to :mod:`sphinx_toolbox.github.issues`:

	* :class:`~.IssueNode`
	* :class:`~.IssueNodeWithName`
	* :func:`~.issue_role`
	* :func:`~.pull_role`
	* :func:`~.visit_issue_node`
	* :func:`~.depart_issue_node`
	* :func:`~.get_issue_title`

.. latex:vspace:: 10px

"""
#
#  Copyright © 2020-2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#
#  Based on pyspecific.py from the Python documentation.
#  Copyright 2008-2014 by Georg Brandl.
#  Licensed under the PSF License 2.0
#
#  Parts of the docstrings based on https://docutils.sourceforge.io/docs/howto/rst-roles.html
#

# 3rd party
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.github.issues import issue_role, pull_role
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = [
		"issue_role",
		"pull_role",
		"setup",
		]


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.issues`.

	.. versionadded:: 1.0.0

	:param app: The Sphinx application.
	"""

	app.setup_extension("sphinx_toolbox.github")

	# Link to GH issue
	app.add_role("issue", issue_role)

	# Link to GH pull request
	app.add_role("pr", pull_role)
	app.add_role("pull", pull_role)

	return {"parallel_read_safe": True}

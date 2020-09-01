=====================
Directives - Shields
=====================

Several shield/badge directives are available, like this one: |demo|

.. |demo| pre-commit-shield::


They function similarly to the ``.. image::`` directives, although not all options are available.
As with the image directive, shields can be used as part of substitutions, e.g.

.. code-block:: rest

	This repository uses pre-commit |pre-commit|

	.. |pre-commit| pre-commit::


All shields have the following options:

.. rst:directive:option:: alt

	Alternative text for the shield, used when the image cannot be displayed or the user uses a screen reader.

.. rst:directive:option:: height
						  width
						  scale

	The height/width/scale of the shield.

.. rst:directive:option:: name

.. rst:directive:option:: class
	:type: string

	Additional CSS class for the shield.
	All shields have the ``sphinx_toolbox_shield`` class by default.



.. rst:directive:: rtfd-shield

	Shield to show the `ReadTheDocs <https://readthedocs.org/>`_ documentation build status.

	.. rst:directive:option:: project

		The name of the project on *ReadTheDocs*.

	.. rst:directive:option:: version

		The documentation version. Default ``latest``.


	**Example**

	.. rest-example::

		.. rtfd-shield::
			:project: sphinx-toolbox


.. rst:directive:: travis-shield

	Shield to show the `Travis CI <https://travis-ci.com/>`_ build status.

	.. rst:directive:option:: username

		The GitHub username. Defaults to :confval:`github_username`.

	.. rst:directive:option:: repository

		The GitHub repository. Defaults to :confval:`github_repository`.

	.. rst:directive:option:: branch

		The branch to show the build status for. Default ``master``.

	.. rst:directive:option:: travis-site

		The Travis CI site, either ``com`` or ``org``. Default ``com``.


	**Example**

	.. rest-example::

		.. travis-shield::


.. rst:directive:: actions-shield

	Shield to show the *GitHub Actions* build status.

	.. rst:directive:option:: username

		The GitHub username. Defaults to :confval:`github_username`.

	.. rst:directive:option:: repository

		The GitHub repository. Defaults to :confval:`github_repository`.

	.. rst:directive:option:: workflow

		The workflow to show the status for.


	**Example**

	.. rest-example::

		.. actions-shield::
			:workflow: Windows Tests


.. rst:directive:: requires-io-shield

	Shield to show the *Requires.io* status.

	.. rst:directive:option:: username

		The GitHub username. Defaults to :confval:`github_username`.

	.. rst:directive:option:: repository

		The GitHub repository. Defaults to :confval:`github_repository`.

	.. rst:directive:option:: branch

		The branch to show the build status for. Default ``master``.


	**Example**

	.. rest-example::

		.. requires-io-shield::


.. rst:directive:: coveralls-shield

	Shield to show the code coverage from `Coveralls.io <https://coveralls.io/>`_.

	.. rst:directive:option:: username

		The GitHub username. Defaults to :confval:`github_username`.

	.. rst:directive:option:: repository

		The GitHub repository. Defaults to :confval:`github_repository`.

	.. rst:directive:option:: branch

		The branch to show the build status for. Default ``master``.


	**Example**

	.. rest-example::

		.. coveralls-shield::


.. rst:directive:: codefactor-shield

	Shield to show the code quality from `Codefactor <https://www.codefactor.io>`_.

	.. rst:directive:option:: username

		The GitHub username. Defaults to :confval:`github_username`.

	.. rst:directive:option:: repository

		The GitHub repository. Defaults to :confval:`github_repository`.


	**Example**

	.. rest-example::

		.. codefactor-shield::


.. rst:directive:: pypi-shield

	Shield to show information about the project on `PyPI <https://pypi.org/>`_.

	.. rst:directive:option:: project

		The name of the project on *PyPI*.

	Only one of the following options is permitted:

	.. rst:directive:option:: version

		Show the package version.

	.. rst:directive:option:: py-versions

		Show the supported python versions.

	.. rst:directive:option:: implementations

		Show the supported python implementations.

	.. rst:directive:option:: wheel

		Show whether the package has a wheel.

	.. rst:directive:option:: license

		Show the license listed on PyPI.

	.. rst:directive:option:: downloads

		Show the downloads for the given period (day / week / month)


	**Examples**

	.. rest-example::

		.. pypi-shield::
			:version:

		.. pypi-shield::
			:project: sphinx
			:downloads: month


.. rst:directive:: github-shield

	Shield to show information about a GitHub repository.

	.. rst:directive:option:: username

		The GitHub username. Defaults to :confval:`github_username`.

	.. rst:directive:option:: repository

		The GitHub repository. Defaults to :confval:`github_repository`.

	.. rst:directive:option:: branch

		The branch to show information about. Default ``master``.

		Required for ``commits-since`` and ``last-commit``.

	Only one of the following options is permitted:

	.. rst:directive:option:: contributors
		:type: flag

		Show the number of contributors.

	.. rst:directive:option:: commits-since: tag
		:type: string

		Show the number of commits since the given tag.

	.. rst:directive:option:: last-commit
		:type: flag

		Show the date of the last commit.

	.. rst:directive:option:: top-language
		:type: flag

		Show the top language and percentage.

	.. rst:directive:option:: license
		:type: flag

		Show the license detected by GitHub.


	**Examples**

	.. rest-example::

		.. github-shield::
			:last-commit:

		.. github-shield::
			:commits-since: v0.1.0


.. rst:directive:: maintained-shield:

	Shield to indicate whether the project is maintained.

	Takes a single argument: the current year.


	**Example**

	.. rest-example::

		.. maintained-shield:: 2020


.. rst:directive:: pre-commit-shield

	Shield to indicate that the project uses `pre-commit <https://pre-commit.com/>`_.


	**Example**

	.. rest-example::

		.. pre-commit-shield::

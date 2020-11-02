###############
sphinx-toolbox
###############

.. start short_desc

**Box of handy tools for Sphinx 🧰 📔**

.. end short_desc


.. start shields

.. list-table::
	:stub-columns: 1
	:widths: 10 90

	* - Docs
	  - |docs| |docs_check|
	* - Tests
	  - |travis| |actions_windows| |actions_macos| |coveralls| |codefactor| |pre_commit_ci|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained|
	* - Other
	  - |license| |language| |requires| |pre_commit|

.. |docs| image:: https://img.shields.io/readthedocs/sphinx-toolbox/latest?logo=read-the-docs
	:target: https://sphinx-toolbox.readthedocs.io/en/latest/?badge=latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/domdfcoding/sphinx-toolbox/workflows/Docs%20Check/badge.svg
	:target: https://github.com/domdfcoding/sphinx-toolbox/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |travis| image:: https://img.shields.io/travis/com/domdfcoding/sphinx-toolbox/master?logo=travis
	:target: https://travis-ci.com/domdfcoding/sphinx-toolbox
	:alt: Travis Build Status

.. |actions_windows| image:: https://github.com/domdfcoding/sphinx-toolbox/workflows/Windows%20Tests/badge.svg
	:target: https://github.com/domdfcoding/sphinx-toolbox/actions?query=workflow%3A%22Windows+Tests%22
	:alt: Windows Tests Status

.. |actions_macos| image:: https://github.com/domdfcoding/sphinx-toolbox/workflows/macOS%20Tests/badge.svg
	:target: https://github.com/domdfcoding/sphinx-toolbox/actions?query=workflow%3A%22macOS+Tests%22
	:alt: macOS Tests Status

.. |requires| image:: https://requires.io/github/domdfcoding/sphinx-toolbox/requirements.svg?branch=master
	:target: https://requires.io/github/domdfcoding/sphinx-toolbox/requirements/?branch=master
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/domdfcoding/sphinx-toolbox/master?logo=coveralls
	:target: https://coveralls.io/github/domdfcoding/sphinx-toolbox?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/domdfcoding/sphinx-toolbox?logo=codefactor
	:target: https://www.codefactor.io/repository/github/domdfcoding/sphinx-toolbox
	:alt: CodeFactor Grade

.. |pypi-version| image:: https://img.shields.io/pypi/v/sphinx-toolbox
	:target: https://pypi.org/project/sphinx-toolbox/
	:alt: PyPI - Package Version

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/sphinx-toolbox?logo=python&logoColor=white
	:target: https://pypi.org/project/sphinx-toolbox/
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/sphinx-toolbox
	:target: https://pypi.org/project/sphinx-toolbox/
	:alt: PyPI - Supported Implementations

.. |wheel| image:: https://img.shields.io/pypi/wheel/sphinx-toolbox
	:target: https://pypi.org/project/sphinx-toolbox/
	:alt: PyPI - Wheel

.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/sphinx-toolbox?logo=anaconda
	:target: https://anaconda.org/domdfcoding/sphinx-toolbox
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/sphinx-toolbox?label=conda%7Cplatform
	:target: https://anaconda.org/domdfcoding/sphinx-toolbox
	:alt: Conda - Platform

.. |license| image:: https://img.shields.io/github/license/domdfcoding/sphinx-toolbox
	:target: https://github.com/domdfcoding/sphinx-toolbox/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/domdfcoding/sphinx-toolbox
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/domdfcoding/sphinx-toolbox/v1.7.1
	:target: https://github.com/domdfcoding/sphinx-toolbox/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/domdfcoding/sphinx-toolbox
	:target: https://github.com/domdfcoding/sphinx-toolbox/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2020
	:alt: Maintenance

.. |pre_commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
	:target: https://github.com/pre-commit/pre-commit
	:alt: pre-commit

.. |pre_commit_ci| image:: https://results.pre-commit.ci/badge/github/domdfcoding/sphinx-toolbox/master.svg
	:target: https://results.pre-commit.ci/latest/github/domdfcoding/sphinx-toolbox/master
	:alt: pre-commit.ci status

.. end shields

|

Installation
--------------

.. start installation

``sphinx-toolbox`` can be installed from PyPI or Anaconda.

To install with ``pip``:

.. code-block:: bash

	$ python -m pip install sphinx-toolbox

To install with ``conda``:

	* First add the required channels

	.. code-block:: bash

		$ conda config --add channels http://conda.anaconda.org/domdfcoding
		$ conda config --add channels http://conda.anaconda.org/conda-forge

	* Then install

	.. code-block:: bash

		$ conda install sphinx-toolbox

.. end installation

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
	  - |actions_linux| |actions_windows| |actions_macos| |coveralls|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained| |pypi-downloads|
	* - QA
	  - |codefactor| |actions_flake8| |actions_mypy|
	* - Other
	  - |license| |language| |requires|

.. |docs| image:: https://img.shields.io/readthedocs/sphinx-toolbox/latest?logo=read-the-docs
	:target: https://sphinx-toolbox.readthedocs.io/en/latest
	:alt: Documentation Build Status

.. |docs_check| image:: https://github.com/sphinx-toolbox/sphinx-toolbox/workflows/Docs%20Check/badge.svg
	:target: https://github.com/sphinx-toolbox/sphinx-toolbox/actions?query=workflow%3A%22Docs+Check%22
	:alt: Docs Check Status

.. |actions_linux| image:: https://github.com/sphinx-toolbox/sphinx-toolbox/workflows/Linux/badge.svg
	:target: https://github.com/sphinx-toolbox/sphinx-toolbox/actions?query=workflow%3A%22Linux%22
	:alt: Linux Test Status

.. |actions_windows| image:: https://github.com/sphinx-toolbox/sphinx-toolbox/workflows/Windows/badge.svg
	:target: https://github.com/sphinx-toolbox/sphinx-toolbox/actions?query=workflow%3A%22Windows%22
	:alt: Windows Test Status

.. |actions_macos| image:: https://github.com/sphinx-toolbox/sphinx-toolbox/workflows/macOS/badge.svg
	:target: https://github.com/sphinx-toolbox/sphinx-toolbox/actions?query=workflow%3A%22macOS%22
	:alt: macOS Test Status

.. |actions_flake8| image:: https://github.com/sphinx-toolbox/sphinx-toolbox/workflows/Flake8/badge.svg
	:target: https://github.com/sphinx-toolbox/sphinx-toolbox/actions?query=workflow%3A%22Flake8%22
	:alt: Flake8 Status

.. |actions_mypy| image:: https://github.com/sphinx-toolbox/sphinx-toolbox/workflows/mypy/badge.svg
	:target: https://github.com/sphinx-toolbox/sphinx-toolbox/actions?query=workflow%3A%22mypy%22
	:alt: mypy status

.. |requires| image:: https://requires.io/github/sphinx-toolbox/sphinx-toolbox/requirements.svg?branch=master
	:target: https://requires.io/github/sphinx-toolbox/sphinx-toolbox/requirements/?branch=master
	:alt: Requirements Status

.. |coveralls| image:: https://img.shields.io/coveralls/github/sphinx-toolbox/sphinx-toolbox/master?logo=coveralls
	:target: https://coveralls.io/github/sphinx-toolbox/sphinx-toolbox?branch=master
	:alt: Coverage

.. |codefactor| image:: https://img.shields.io/codefactor/grade/github/sphinx-toolbox/sphinx-toolbox?logo=codefactor
	:target: https://www.codefactor.io/repository/github/sphinx-toolbox/sphinx-toolbox
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

.. |license| image:: https://img.shields.io/github/license/sphinx-toolbox/sphinx-toolbox
	:target: https://github.com/sphinx-toolbox/sphinx-toolbox/blob/master/LICENSE
	:alt: License

.. |language| image:: https://img.shields.io/github/languages/top/sphinx-toolbox/sphinx-toolbox
	:alt: GitHub top language

.. |commits-since| image:: https://img.shields.io/github/commits-since/sphinx-toolbox/sphinx-toolbox/v2.11.0
	:target: https://github.com/sphinx-toolbox/sphinx-toolbox/pulse
	:alt: GitHub commits since tagged version

.. |commits-latest| image:: https://img.shields.io/github/last-commit/sphinx-toolbox/sphinx-toolbox
	:target: https://github.com/sphinx-toolbox/sphinx-toolbox/commit/master
	:alt: GitHub last commit

.. |maintained| image:: https://img.shields.io/maintenance/yes/2021
	:alt: Maintenance

.. |pypi-downloads| image:: https://img.shields.io/pypi/dm/sphinx-toolbox
	:target: https://pypi.org/project/sphinx-toolbox/
	:alt: PyPI - Downloads

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

		$ conda config --add channels https://conda.anaconda.org/conda-forge
		$ conda config --add channels https://conda.anaconda.org/domdfcoding

	* Then install

	.. code-block:: bash

		$ conda install sphinx-toolbox

.. end installation

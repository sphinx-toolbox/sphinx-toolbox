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
	  - |actions_linux| |actions_windows| |actions_macos| |coveralls| |codefactor| |pre_commit_ci|
	* - PyPI
	  - |pypi-version| |supported-versions| |supported-implementations| |wheel|
	* - Anaconda
	  - |conda-version| |conda-platform|
	* - Activity
	  - |commits-latest| |commits-since| |maintained|
	* - Other
	  - |license| |language| |requires| |pre_commit|

.. |docs| rtfd-shield::
	:project: sphinx-toolbox
	:alt: Documentation Build Status

.. |docs_check| actions-shield::
	:workflow: Docs Check
	:alt: Docs Check Status

.. |actions_linux| actions-shield::
	:workflow: Linux Tests
	:alt: Linux Test Status

.. |actions_windows| actions-shield::
	:workflow: Windows Tests
	:alt: Windows Test Status

.. |actions_macos| actions-shield::
	:workflow: macOS Tests
	:alt: macOS Test Status

.. |requires| requires-io-shield::
	:alt: Requirements Status

.. |coveralls| coveralls-shield::
	:alt: Coverage

.. |codefactor| codefactor-shield::
	:alt: CodeFactor Grade

.. |pypi-version| pypi-shield::
	:project: sphinx-toolbox
	:version:
	:alt: PyPI - Package Version

.. |supported-versions| pypi-shield::
	:project: sphinx-toolbox
	:py-versions:
	:alt: PyPI - Supported Python Versions

.. |supported-implementations| pypi-shield::
	:project: sphinx-toolbox
	:implementations:
	:alt: PyPI - Supported Implementations

.. |wheel| pypi-shield::
	:project: sphinx-toolbox
	:wheel:
	:alt: PyPI - Wheel

.. |conda-version| image:: https://img.shields.io/conda/v/domdfcoding/sphinx-toolbox?logo=anaconda
	:target: https://anaconda.org/domdfcoding/sphinx-toolbox
	:alt: Conda - Package Version

.. |conda-platform| image:: https://img.shields.io/conda/pn/domdfcoding/sphinx-toolbox?label=conda%7Cplatform
	:target: https://anaconda.org/domdfcoding/sphinx-toolbox
	:alt: Conda - Platform

.. |license| github-shield::
	:license:
	:alt: License

.. |language| github-shield::
	:top-language:
	:alt: GitHub top language

.. |commits-since| github-shield::
	:commits-since: v1.8.2
	:alt: GitHub commits since tagged version

.. |commits-latest| github-shield::
	:last-commit:
	:alt: GitHub last commit

.. |maintained| maintained-shield:: 2020
	:alt: Maintenance

.. |pre_commit| pre-commit-shield::
	:alt: pre-commit

.. |pre_commit_ci| pre-commit-ci-shield::
	:alt: pre-commit.ci status

.. end shields

Installation
--------------

.. start installation

.. installation:: sphinx-toolbox
	:pypi:
	:github:
	:anaconda:
	:conda-channels: domdfcoding, conda-forge

.. end installation


.. toctree::
	:hidden:

	Home<self>


.. toctree::
	:maxdepth: 1
	:caption: Extensions
	:glob:

	extensions/index
	extensions/*

.. toctree::
	:maxdepth: 2
	:glob:

	extensions/**/index


.. toctree::
	:maxdepth: 3
	:caption: Developer API
	:glob:

	api/sphinx-toolbox
	api/*


.. toctree::
	:maxdepth: 3
	:caption: Contributing

	contributing
	Source


.. start links

View the :ref:`Function Index <genindex>` or browse the `Source Code <_modules/index.html>`__.

`Browse the GitHub Repository <https://github.com/domdfcoding/sphinx-toolbox>`__

.. end links


Caching
-----------

HTTP requests to obtain issue/pull request titles are cached for four hours.

To clear the cache manually, run:

.. prompt:: bash

	python3 -m sphinx_toolbox

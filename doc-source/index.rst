###############
sphinx-toolbox
###############

.. start short_desc

.. documentation-summary::
	:meta:

.. end short_desc

.. start shields

.. only:: html

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

	.. |docs| rtfd-shield::
		:project: sphinx-toolbox
		:alt: Documentation Build Status

	.. |docs_check| actions-shield::
		:workflow: Docs Check
		:alt: Docs Check Status

	.. |actions_linux| actions-shield::
		:workflow: Linux
		:alt: Linux Test Status

	.. |actions_windows| actions-shield::
		:workflow: Windows
		:alt: Windows Test Status

	.. |actions_macos| actions-shield::
		:workflow: macOS
		:alt: macOS Test Status

	.. |actions_flake8| actions-shield::
		:workflow: Flake8
		:alt: Flake8 Status

	.. |actions_mypy| actions-shield::
		:workflow: mypy
		:alt: mypy status

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
		:commits-since: v2.13.0b1
		:alt: GitHub commits since tagged version

	.. |commits-latest| github-shield::
		:last-commit:
		:alt: GitHub last commit

	.. |maintained| maintained-shield:: 2021
		:alt: Maintenance

	.. |pypi-downloads| pypi-shield::
		:project: sphinx-toolbox
		:downloads: month
		:alt: PyPI - Downloads

.. end shields

Installation
--------------

.. start installation

.. installation:: sphinx-toolbox
	:pypi:
	:github:
	:anaconda:
	:conda-channels: conda-forge, domdfcoding

.. end installation

Contents
------------

.. phantom-section::


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


.. sidebar-links::
	:caption: Links
	:github:
	:pypi: sphinx-toolbox

	Contributing Guide <https://contributing-to-sphinx-toolbox.readthedocs.io/en/latest/>
	Source


.. start links

.. only:: html

	View the :ref:`Function Index <genindex>` or browse the `Source Code <_modules/index.html>`__.

	:github:repo:`Browse the GitHub Repository <sphinx-toolbox/sphinx-toolbox>`

.. end links

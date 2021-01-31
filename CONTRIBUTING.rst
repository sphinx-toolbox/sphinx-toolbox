==============
Contributing
==============

.. This file based on https://github.com/PyGithub/PyGithub/blob/master/CONTRIBUTING.md

``sphinx-toolbox`` uses `tox <https://tox.readthedocs.io>`_ to automate testing and packaging,
and `pre-commit <https://pre-commit.com>`_ to maintain code quality.

Install ``pre-commit`` with ``pip`` and install the git hook:

.. code-block:: bash

	$ python -m pip install pre-commit
	$ pre-commit install


Coding style
--------------

`formate <https://formate.readthedocs.io>`_ is used for code formatting.

It can be run manually via ``pre-commit``:

.. code-block:: bash

	$ pre-commit run formate -a


Or, to run the complete autoformatting suite:

.. code-block:: bash

	$ pre-commit run -a


Automated tests
-------------------

Tests are run with ``tox`` and ``pytest``.
To run tests for a specific Python version, such as Python 3.6:

.. code-block:: bash

	$ tox -e py36


To run tests for all Python versions, simply run:

.. code-block:: bash

	$ tox


Type Annotations
-------------------

Type annotations are checked using ``mypy``. Run ``mypy`` using ``tox``:

.. code-block:: bash

	$ tox -e mypy



Build documentation locally
------------------------------

The documentation is powered by Sphinx. A local copy of the documentation can be built with ``tox``:

.. code-block:: bash

	$ tox -e docs

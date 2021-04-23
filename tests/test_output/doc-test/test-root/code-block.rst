:orphan:

=====================================
sphinx-toolbox Demo - Code
=====================================

.. code-block:: python

	def print(text):
		sys.stdout.write(text)


.. code-block:: python
	:tab-width: 4

	def print(text):
		sys.stdout.write(text)


.. code-block:: python
	:tab-width: 8

	def print(text):
		sys.stdout.write(text)


.. code-block:: python
	:dedent: 4

		def print(text):
			sys.stdout.write(text)

.. code-block:: python
	:linenos:

	def print(text):
		sys.stdout.write(text)

Code Cell
-----------

.. code-cell:: python
	:execution-count: 1

	def print(text):
		sys.stdout.write(text)

	print("hello world")

.. output-cell::
	:execution-count: 1

	hello world

.. code-cell:: python
	:execution-count: 2
	:tab-width: 8

	def print(text):
		sys.stdout.write(text)

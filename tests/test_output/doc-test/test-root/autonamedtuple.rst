:orphan:

=====================================
sphinx-toolbox Demo - AutoNamedTuple
=====================================

.. automodule:: autonamedtuple_demo
	:members:
	:exclude-members: Movie

.. autonamedtuple:: autonamedtuple_demo.Movie

.. autonamedtuple:: autonamedtuple_demo.Foo
	:show-inheritance:

.. autonamedtuple:: autonamedtuple_demo.Traditional
	:show-inheritance:

.. autonamedtuple:: autonamedtuple_demo.NoDocstring
	:show-inheritance:

.. autonamedtuple:: autonamedtuple_demo.NoDocstring
	:noindex:

.. autonamedtuple:: autonamedtuple_demo.CustomisedNew

This function takes a single argument, the :namedtuple:`~.Movie` to watch.
The name of the movie can be accessed with the :namedtuple-field:`~.Movie.name` attribute.

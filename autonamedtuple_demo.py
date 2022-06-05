# Examples from
# https://docs.python.org/3/library/typing.html#typing.NamedTuple
# https://www.python.org/dev/peps/pep-0589/#totality
# https://github.com/python/typing/pull/700

# stdlib
import collections
from typing import NamedTuple

__all__ = ("Animal", "Employee", "Movie")


class Animal(NamedTuple):
	"""
	An animal.

	:param name: The name of the animal.
	:param voice: The animal's voice.
	"""

	name: str
	voice: str


class Employee(NamedTuple):
	"""
	Represents an employee.

	:param id: The employee's ID number
	"""

	#: The employee's name
	name: str

	id: int = 3

	def __repr__(self) -> str:
		return f'<Employee {self.name}, id={self.id}>'

	def is_executive(self) -> bool:
		"""
		Returns whether the employee is an executive.

		Executives have ID numbers < 10.
		"""


class Movie(NamedTuple):
	"""
	Represents a movie.
	"""

	#: The name of the movie.
	name: str

	#: The movie's release year.
	year: int

	based_on: str


class Foo(NamedTuple):
	"""
	A Namedtuple

	:param a: An integer
	:param str b: A string
	:param str c:
	"""

	#: An integer (another doc)
	a: int

	b: str

	#: C's doc
	c: str


class NoDocstring(NamedTuple):
	#: An integer
	a: int

	b: str

	#: C's doc
	c: str


Traditional = collections.namedtuple("Traditional", "a, b, c")
Traditional.__doc__ = "A traditional Namedtuple"


class CustomisedNew(collections.namedtuple("CustomisedNew", "a, b, c")):

	def __new__(cls, values: str):
		return super().__new__(*values.split())

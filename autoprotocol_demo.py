# stdlib
from abc import abstractmethod
from typing import Any, TypeVar

# 3rd party
from domdf_python_tools.doctools import prettify_docstrings
from typing_extensions import Protocol, runtime_checkable

__all__ = ("HasLessThan", "HasGreaterThan", "Frobnicater")


@prettify_docstrings
class HasLessThan(Protocol):
	"""
	:class:`typing.Protocol` for classes that support the ``<`` operator.
	"""

	def __lt__(self, other) -> bool: ...


@prettify_docstrings
class HasGreaterThan(Protocol):

	def __gt__(self, other) -> bool: ...


@runtime_checkable
class Frobnicater(Protocol):

	def frobnicate(self, something) -> Any: ...


# From https://github.com/python/cpython/blob/main/Lib/typing.py

T_co = TypeVar("T_co", covariant=True)  # Any type covariant containers.


@runtime_checkable
class SupportsAbs(Protocol[T_co]):
	"""
	An ABC with one abstract method __abs__ that is covariant in its return type.
	"""

	__slots__ = ()

	@abstractmethod
	def __abs__(self) -> T_co:
		pass

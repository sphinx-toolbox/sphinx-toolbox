# stdlib
from typing import Any

# 3rd party
from domdf_python_tools.doctools import prettify_docstrings
from typing_extensions import Protocol, runtime_checkable

__all__ = ["HasLessThan", "HasGreaterThan", "Frobnicater"]


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

# stdlib
from typing import Any

# 3rd party
from typing_extensions import Protocol, runtime_checkable


class HasLessThan(Protocol):
	"""
	:class:`typing.Protocol` for classes that support the ``<`` operator.
	"""

	def __lt__(self, other) -> bool:
		...


class HasGreaterThan(Protocol):

	def __gt__(self, other) -> bool:
		...


@runtime_checkable
class Frobnicater(Protocol):

	def frobnicate(self, something) -> Any:
		...

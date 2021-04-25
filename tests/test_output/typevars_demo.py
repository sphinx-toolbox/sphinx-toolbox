# stdlib
from typing import TypeVar

# 3rd party
import attr

__all__ = [
		"Demo",
		"SlotsDemo",
		'T',
		"T_co",
		"T_contra",
		'S',
		"DS",
		"FR",
		]

FR = TypeVar("FR", bound="SlotsDemo")


@attr.s(slots=False)
class Demo:
	"""
	An attrs class
	"""

	#: An argument
	arg1: str = attr.ib()

	#: Another argument
	arg2: int = attr.ib()


@attr.s(slots=True)
class SlotsDemo:
	"""
	An attrs class with slots=True
	"""

	#: An argument
	arg1: str = attr.ib()

	#: Another argument
	arg2: int = attr.ib()


T = TypeVar('T')
T_co = TypeVar("T_co", covariant=True)
T_contra = TypeVar("T_contra", contravariant=True)
S = TypeVar('S', bound=SlotsDemo)
DS = TypeVar("DS", SlotsDemo, Demo)

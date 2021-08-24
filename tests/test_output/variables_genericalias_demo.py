# stdlib
import os
import pathlib
from typing import Callable, List, Tuple, Union

# 3rd party
import attr

#: Some variable
variable: Union[List[str], Tuple[str, int, float], int, bytes, Callable[[str], int]] = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

CONSTANT: int = 42
"""
Don't change this!"
"""

#: Type hint for filesystem paths
PathLike = Union[str, os.PathLike, pathlib.Path]


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

# stdlib
from typing import Callable, List, Tuple, Union

#: Some type alias
VarType = Union[List[str], Tuple[str, int, float], int, bytes, Callable[[str], int]]

#: Some variable
VARIABLE: VarType = ['a', 'b', 'c', 'd', 'e', 'f', 'g']

CONSTANT: int = 42
"""
Don't change this!"
"""

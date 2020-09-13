# stdlib
import os
import pathlib
from typing import Callable, List, Tuple, Union

#: Some variable
variable: Union[List[str], Tuple[str, int, float], int, bytes, Callable[[str], int]] = ["a", "b", "c", "d", "e", "f", "g"]


CONSTANT: int = 42
"""
Don't change this!"
"""


#: Type hint for filesystem paths
PathLike = Union[str, os.PathLike, pathlib.Path]
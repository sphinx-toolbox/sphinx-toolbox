from __future__ import annotations

# stdlib
from typing import Callable, NamedTuple

# Examples from
# https://docs.python.org/3/library/typing.html#typing.NamedTuple
# https://www.python.org/dev/peps/pep-0589/#totality
# https://github.com/python/typing/pull/700

__all__ = ["Animal"]


class Animal(NamedTuple):
	"""
	An animal.

	:param name: The name of the animal.
	:param voice: The animal's voice.
	"""

	name: str
	voice: Callable[[], str]

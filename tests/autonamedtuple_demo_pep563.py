# Examples from
# https://docs.python.org/3/library/typing.html#typing.NamedTuple
# https://www.python.org/dev/peps/pep-0589/#totality
# https://github.com/python/typing/pull/700

# stdlib
import sys

__all__ = ["Animal"]

if sys.version_info < (3, 7):

	# stdlib
	from typing import Callable, NamedTuple

	class Animal(NamedTuple):
		"""
		An animal.

		:param name: The name of the animal.
		:param voice: The animal's voice.
		"""

		name: str
		voice: "Callable[[], str]"

else:
	# this package
	from tests._autonamedtuple_demo_pep563 import Animal

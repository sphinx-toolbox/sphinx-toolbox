# Examples from
# https://www.python.org/dev/peps/pep-0589/#totality
# https://github.com/python/typing/pull/700
"""
Demo of ``.. autotypeddict::``
"""

# 3rd party
from typing_extensions import TypedDict

__all__ = ("Movie", "Animal", "OldStyleAnimal", "Cat", "Bird", "AquaticBird")


class Movie(TypedDict):
	"""
	Represents a movie.
	"""

	#: The name of the movie.
	name: str

	#: The movie's release year.
	year: int

	based_on: str


class _Animal(TypedDict):
	"""
	Keys required by all animals.
	"""

	#: The name of the animal
	name: str


class Animal(_Animal, total=False):
	"""
	Optional keys common to all animals.
	"""

	#: The animal's voice.
	voice: str


#: Old style TypedDict for Python 2 and where keys aren't valid Python identifiers.
OldStyleAnimal = TypedDict(
		"OldStyleAnimal", {
				"animal-name": str,
				"animal-voice": str,
				}, total=False
		)


class Cat(Animal):
	"""
	A cat.
	"""

	#: The colour of the cat's fur.
	fur_color: str


class Bird(Animal):
	"""
	A bird.
	"""

	#: The size of the bird's egg, in mm.
	egg_size: float


class AquaticBird(Bird):

	#: The bird's habitat (e.g. lake, sea)
	habitat: float

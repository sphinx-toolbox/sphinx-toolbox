# stdlib
from typing import Callable, List, Optional, Type, Union, overload

__all__ = ["serde", "Foo", "Bar"]


@overload
def serde(cls: Type[object], from_key: str = ..., to_key: str = ...) -> Type[object]: ...  # pragma: no cover


@overload
def serde(cls: None = None, from_key: str = ..., to_key: str = ...) -> "Callable[[Type[object]], Type[object]]": ...  # pragma: no cover


def serde(
		cls: Optional[Type[object]] = None,
		from_key: str = "from",
		to_key: str = "to",
		) -> Union[Type[object], Callable[[Type[object]], Type[object]]]:
	r"""
	Decorator to add serialisation and deserialisation capabilities to attrs classes.

	:param cls: The attrs class to add the methods to.
	:param from_key:
	:param to_key:

	:rtype:

	Classes decorated with :deco:`~attr_utils.serialise.serde` will have two new methods added:

	.. py:classmethod:: from_dict(d)

		Construct an instance of the class from a dictionary.

		:param d: :class:`~typing.Mapping`\[:class:`str`, :py:obj:`~typing.Any`\]

	.. py:method:: to_dict() -> MutableMapping[str, Any]:

		Returns a dictionary containing the contents of the class.

		:rtype: :class:`~typing.MutableMapping`\[:class:`str`, :py:obj:`~typing.Any`\]

	"""


class Foo:

	@overload
	def __getitem__(self, item: int) -> str: ...

	@overload
	def __getitem__(self, item: slice) -> List[str]: ...

	def __getitem__(self, item: Union[int, slice]) -> Union[str, List[str]]:
		"""
		Return the item with the given index.

		:param item:

		:rtype:

		.. versionadded:: 1.2.3
		"""


class Bar:

	@overload
	def __getitem__(self, item: int) -> str: ...

	@overload
	def __getitem__(self, item: slice) -> List[str]: ...

	def __getitem__(self, item: Union[int, slice]) -> Union[str, List[str]]:
		"""
		Return the item with the given index.

		.. versionadded:: 1.2.3

		:param item:
		"""

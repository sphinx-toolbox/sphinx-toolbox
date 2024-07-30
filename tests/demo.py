def ellipsis_function(foo: str = ...) -> int: ...  # type: ignore[empty-body]


def ellipsis_function_2(foo: str = ..., *args: int, **kwargs: str) -> int:  # type: ignore[empty-body]
	r"""
	A function with ellipses in the docstring.

	:param foo:
	:param \*args:
	:param \*\*kwargs:
	"""

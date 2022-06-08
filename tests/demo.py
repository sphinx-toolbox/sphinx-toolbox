def ellipsis_function(foo: str = ...) -> int: ...


def ellipsis_function_2(foo: str = ..., *args: int, **kwargs: str) -> int:
	r"""
	A function with ellipses in the docstring.

	:param foo:
	:param \*args:
	:param \*\*kwargs:
	"""

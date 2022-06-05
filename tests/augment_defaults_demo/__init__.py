class Foo:
	"""
	I am ``Foo``.
	"""

	def __init__(self):
		"""
		This is ``__init__``
		"""

	def excluded(self):  # noqa: MAN002
		"""
		I should be excluded.
		"""

	def function(self):  # noqa: MAN002
		"""
		I shouldn't be excluded.
		"""

	def __repr__(self):  # noqa: MAN002
		"""
		This is ``__repr__``
		"""

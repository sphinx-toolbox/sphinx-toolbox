class Foo:
	"""
	I am ``Foo``.
	"""

	def __init__(self):
		"""
		This is ``__init__``
		"""

	def excluded(self):
		"""
		I should be excluded.
		"""

	def function(self):
		"""
		I shouldn't be excluded.
		"""

	def __repr__(self):
		"""
		This is ``__repr__``
		"""

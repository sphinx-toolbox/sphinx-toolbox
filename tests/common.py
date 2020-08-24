class AttrDict(dict):

	def __getattr__(self, item):
		return self[item]

	def __setattr__(self, item, value):
		self[item] = value

# stdlib
from typing import Union

# 3rd party
from apeye.slumber_url import SlumberURL
from domdf_python_tools.secrets import Secret


class OctoAPI:
	"""
	The primary interface to the Octopus Energy API.

	:param api_key: API key to access the Octopus Energy API.

	If you are an Octopus Energy customer, you can generate an API key from your
	`online dashboard <https://octopus.energy/dashboard/developer/>`_.
	"""

	def __init__(self, api_key: str):

		#: The API key to access the Octopus Energy API.
		self.API_KEY: Union[Secret, str, float] = Secret(api_key)

		#: The base URL of the Octopus Energy API.
		self.API_BASE: "SlumberURL" = SlumberURL("https://api.octopus.energy/v1", auth=(self.API_KEY.value, ''))

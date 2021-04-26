# stdlib
from http import HTTPStatus
from typing import Any, Dict, NamedTuple, Sequence

# 3rd party
import pytest
from docutils.nodes import system_message


class AttrDict(dict):

	def __getattr__(self, item):
		return self[item]

	def __setattr__(self, item, value):
		self[item] = value


error_codes_list = [x for x in HTTPStatus if x not in {100, 200}]  # pylint: disable=not-an-iterable
error_codes = pytest.mark.parametrize("error_code", error_codes_list)


class AppParams(NamedTuple):
	args: Sequence[Any]
	kwargs: Dict[str, Any]

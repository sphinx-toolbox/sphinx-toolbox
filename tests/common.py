# stdlib
from http import HTTPStatus
from typing import Any, Dict, NamedTuple, Sequence, Tuple

# 3rd party
import pytest
import sphinx


class AttrDict(dict):

	def __getattr__(self, item):  # noqa: MAN001,MAN002
		try:
			return self[item]
		except KeyError as e:
			raise AttributeError(str(e))

	def __setattr__(self, item, value):  # noqa: MAN001,MAN002
		self[item] = value


error_codes_list = [x for x in HTTPStatus if x not in {100, 200}]  # pylint: disable=not-an-iterable
error_codes = pytest.mark.parametrize("error_code", error_codes_list)


class AppParams(NamedTuple):
	args: Sequence[Any]
	kwargs: Dict[str, Any]


def get_app_config_values(config: Any) -> Tuple[str, str, Any]:
	if sphinx.version_info >= (7, 3):
		# valid_types =
		valid_types = config.valid_types
		if isinstance(valid_types, (set, frozenset)):
			valid_types = list(valid_types)
		return (config.default, config.rebuild, valid_types)
	else:
		return config

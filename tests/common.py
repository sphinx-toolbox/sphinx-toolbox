# stdlib
from http import HTTPStatus
from types import SimpleNamespace
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
		valid_types = config.valid_types
		default = config.default
		rebuild = config.rebuild
	else:
		default, rebuild, valid_types = config

	if isinstance(valid_types, (set, frozenset, tuple, list)):
		valid_types = sorted(valid_types)

	if hasattr(valid_types, "_candidates"):
		new_valid_types = SimpleNamespace()
		new_valid_types.candidates = sorted(valid_types._candidates)
		valid_types = new_valid_types

	return (default, rebuild, valid_types)

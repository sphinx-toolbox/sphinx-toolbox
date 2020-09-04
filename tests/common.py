# stdlib
from http import HTTPStatus
from typing import Any, Dict, NamedTuple, Sequence

# 3rd party
import pytest
from bs4 import BeautifulSoup  # type: ignore
from docutils.nodes import system_message
from pytest_regressions.file_regression import FileRegressionFixture  # type: ignore


class AttrDict(dict):

	def __getattr__(self, item):
		return self[item]

	def __setattr__(self, item, value):
		self[item] = value


error_codes_list = [x for x in HTTPStatus if x not in {100, 200}]  # pylint: disable=not-an-iterable
error_codes = pytest.mark.parametrize("error_code", error_codes_list)


def info(message):
	print(f"INFO: {message}")
	return system_message(message)


def warning(message):
	print(f"WARNING: {message}")
	return system_message(message)


def error(message):
	print(f"ERROR: {message}")
	return system_message(message)


def severe(message):
	print(f"SEVERE: {message}")
	return system_message(message)


class AppParams(NamedTuple):
	args: Sequence[Any]
	kwargs: Dict[str, Any]


def remove_html_footer(page: BeautifulSoup) -> BeautifulSoup:
	for div in page.select("div.footer"):
		div.extract()

	return page


def check_html_regression(page: BeautifulSoup, file_regression: FileRegressionFixture):
	file_regression.check(contents=remove_html_footer(page).prettify(), extension=".html", encoding="UTF-8")

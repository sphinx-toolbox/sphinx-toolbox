# stdlib
import os
import re

# 3rd party
import sphinx


def test_sphinx_version_against_tox():
	m = re.match(r"py.*-sphinx(\d)\.(\d)", os.getenv("TOX_ENV_NAME", ''))
	if m is not None:
		target_version = tuple(map(int, m.groups()))
		assert target_version == sphinx.version_info[:2]

# stdlib
import re

# 3rd party
import pytest


@pytest.mark.parametrize(
		"module", [
				"autodoc_augment_defaults",
				"autodoc_helpers",
				"autodoc_typehints",
				"autoprotocol",
				"autotypeddict",
				]
		)
def test_deprecations(module: str):
	# if f"sphinx_toolbox.{module}" in sys.modules:
	# 	del sys.modules[f"sphinx_toolbox.{module}"]

	with pytest.warns(DeprecationWarning) as record:
		__import__(f"sphinx_toolbox.{module}")

	# check that only one warning was raised
	assert len(record) == 1
	# check that the message matches
	assert re.match(
			fr"Importing from 'sphinx_toolbox\.{module}' is deprecated since 0\.6\.0 and "
			r"the module will be removed in 1\.0\.0\.\nImport from 'sphinx_toolbox"
			r"\.more_autodoc\..*' instead\.",
			record[0].message.args[0],
			)


@pytest.mark.parametrize(
		"module", [
				"patched_autosummary",
				]
		)
def test_deprecations_more_autosummary(module: str):

	with pytest.warns(DeprecationWarning) as record:
		__import__(f"sphinx_toolbox.{module}")

	# check that only one warning was raised
	assert len(record) == 1
	print(record[0].message.args[0])
	# check that the message matches
	assert re.match(
			fr"Importing from 'sphinx_toolbox\.{module}' is deprecated since 0\.7\.0 and "
			r"the module will be removed in 1\.0\.0\.\nImport from 'sphinx_toolbox"
			r"\.more_autosummary' instead\.",
			record[0].message.args[0],
			)

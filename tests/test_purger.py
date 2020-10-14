# 3rd party
import pytest

# this package
from sphinx_toolbox.utils import Purger


class MockBuildEnvironment:
	pass


demo_purger = Purger("all_demo_nodes")


@pytest.mark.parametrize(
		"nodes, output",
		[
				([], []),
				([{"docname": "document"}], []),
				([{"docname": "foo"}], [{"docname": "foo"}]),
				([{"docname": "foo"}, {"docname": "document"}], [{"docname": "foo"}]),
				]
		)
def test_purge_extras_require(nodes, output):
	env = MockBuildEnvironment()

	demo_purger.purge_nodes('', env, "document")  # type: ignore
	assert not hasattr(env, "all_extras_requires")

	env.all_demo_nodes = nodes  # type: ignore
	demo_purger.purge_nodes('', env, "document")  # type: ignore
	assert hasattr(env, "all_demo_nodes")
	assert env.all_demo_nodes == output  # type: ignore

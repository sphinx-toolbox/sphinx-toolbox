# this package
from sphinx_toolbox.rest_example import make_rest_example
from tests.common import AttrDict


class FakeBuildEnvironment(AttrDict):

	def __init__(self, tab_width: int):
		config = AttrDict({"docutils_tab_width": tab_width})
		super().__init__({"config": config})


def test_make_rest_example():

	assert make_rest_example(
			{},
			FakeBuildEnvironment(4),  # type: ignore
			[],
			) == [".. code-block:: rest", '']

	assert make_rest_example(
			{"hello": "world"},
			FakeBuildEnvironment(4),  # type: ignore
			[],
			) == [".. code-block:: rest", "    :hello: world", '']

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(4),  # type: ignore
			[],
			) == [".. code-block:: rest", "    :hello: world", "    :flag:", '']

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(4),  # type: ignore
			["this is some content"],
			) == [
					".. code-block:: rest",
					"    :hello: world",
					"    :flag:",
					'',
					"    this is some content",
					'',
					"this is some content",
					'',
					]

	assert make_rest_example(
			{},
			FakeBuildEnvironment(8),  # type: ignore
			[],
			) == [".. code-block:: rest", '']

	assert make_rest_example(
			{"hello": "world"},
			FakeBuildEnvironment(8),  # type: ignore
			[],
			) == [".. code-block:: rest", "        :hello: world", '']

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(8),  # type: ignore
			[],
			) == [
					".. code-block:: rest",
					"        :hello: world",
					"        :flag:",
					'',
					]

	assert make_rest_example(
			{"hello": "world", "flag": None},
			FakeBuildEnvironment(8),  # type: ignore
			["this is some content"],
			) == [
					".. code-block:: rest",
					"        :hello: world",
					"        :flag:",
					'',
					"        this is some content",
					'',
					"this is some content",
					'',
					]

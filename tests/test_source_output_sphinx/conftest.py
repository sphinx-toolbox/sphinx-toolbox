# stdlib
from typing import Any, Dict, Tuple

# 3rd party
import pytest
from bs4 import BeautifulSoup
from domdf_python_tools.paths import PathPlus
from sphinx.testing.fixtures import app as sphinx_src_app
from sphinx.testing.fixtures import make_app, shared_result, sphinx_test_tempdir, test_params
from sphinx.testing.path import path

# this package
from tests.common import AppParams

fixtures = [make_app, shared_result, sphinx_test_tempdir, test_params, sphinx_src_app]


@pytest.fixture()
def rootdir():
	rdir = PathPlus(__file__).parent.absolute() / "sphinx-doc-test"
	(rdir / "test-sphinx-root").maybe_make(parents=True)
	return path(rdir)


@pytest.fixture
def app_params(
		request: Any,
		test_params: Dict,
		sphinx_test_tempdir: path,
		rootdir: path,
		) -> Tuple[Dict, Dict]:
	"""
	parameters that is specified by 'pytest.mark.sphinx' for
	sphinx.application.Sphinx initialization
	"""

	# ##### process pytest.mark.sphinx

	if hasattr(request.node, 'iter_markers'):  # pytest-3.6.0 or newer
		markers = request.node.iter_markers("sphinx")
	else:
		markers = request.node.get_marker("sphinx")
	pargs = {}
	kwargs: Dict[str, Any] = {}

	if markers is not None:
		# to avoid stacking positional args
		for info in reversed(list(markers)):
			for i, a in enumerate(info.args):
				pargs[i] = a
			kwargs.update(info.kwargs)

	args = [pargs[i] for i in sorted(pargs.keys())]

	# ##### prepare Application params

	testroot = 'sphinx-root'
	kwargs['srcdir'] = srcdir = sphinx_test_tempdir / kwargs.get('srcdir', testroot)

	# special support for sphinx/tests
	if rootdir and not srcdir.exists():
		testroot_path = rootdir / 'test-sphinx-root'
		testroot_path.copytree(srcdir)

	return AppParams(args, kwargs)


@pytest.fixture()
def sphinx_source_page(sphinx_src_app, request) -> BeautifulSoup:
	sphinx_src_app.build(force_all=True)

	pagename = request.param
	c = (sphinx_src_app.outdir / pagename).read_text()

	yield BeautifulSoup(c, "html5lib")

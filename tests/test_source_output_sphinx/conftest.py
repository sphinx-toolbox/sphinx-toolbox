#  Based on Sphinx
#  Copyright (c) 2007-2020 by the Sphinx team.
#  |  All rights reserved.
#  |
#  |  Redistribution and use in source and binary forms, with or without
#  |  modification, are permitted provided that the following conditions are
#  |  met:
#  |
#  |  * Redistributions of source code must retain the above copyright
#  |    notice, this list of conditions and the following disclaimer.
#  |
#  |  * Redistributions in binary form must reproduce the above copyright
#  |    notice, this list of conditions and the following disclaimer in the
#  |    documentation and/or other materials provided with the distribution.
#  |
#  |  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  |  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  |  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  |  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  |  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  |  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  |  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  |  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  |  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  |  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  |  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
import pathlib
import shutil
from typing import Any, Dict, Sequence, Tuple

# 3rd party
import pytest
from bs4 import BeautifulSoup  # type: ignore[import-untyped]
from domdf_python_tools.paths import PathPlus
from sphinx.application import Sphinx
from sphinx.testing.fixtures import app as sphinx_src_app
from sphinx.testing.fixtures import make_app, shared_result, sphinx_test_tempdir, test_params

# this package
from tests.common import AppParams

fixtures = [make_app, shared_result, sphinx_test_tempdir, test_params, sphinx_src_app]


@pytest.fixture()
def rootdir() -> PathPlus:
	rdir = PathPlus(__file__).parent.absolute() / "sphinx-doc-test"
	(rdir / "test-sphinx-root").maybe_make(parents=True)
	return PathPlus(rdir)


@pytest.fixture()
def app_params(
		request: Any,
		test_params: Dict,
		sphinx_test_tempdir: pathlib.Path,
		rootdir: pathlib.Path,
		) -> Tuple[Sequence, Dict]:
	"""
	parameters that is specified by 'pytest.mark.sphinx' for
	sphinx.application.Sphinx initialization
	"""

	# ##### process pytest.mark.sphinx

	markers = request.node.iter_markers("sphinx")
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

	testroot = "sphinx-root"
	kwargs["srcdir"] = srcdir = sphinx_test_tempdir / kwargs.get("srcdir", testroot)

	# special support for sphinx/tests
	if rootdir and not srcdir.exists():
		testroot_path = rootdir / "test-sphinx-root"
		shutil.copytree(testroot_path, srcdir)

	return AppParams(args, kwargs)


@pytest.fixture()
def sphinx_source_page(sphinx_src_app: Sphinx, request) -> BeautifulSoup:
	sphinx_src_app.build(force_all=True)

	pagename = request.param
	c = (sphinx_src_app.outdir / pagename).read_text()

	soup = BeautifulSoup(c, "html5lib")

	for meta in soup.find_all("meta"):
		if meta.get("content", '') == "width=device-width, initial-scale=0.9, maximum-scale=0.9":
			meta.extract()

	return soup

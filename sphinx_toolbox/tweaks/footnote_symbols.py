#!/usr/bin/env python3
#
#  footnote_symbols.py
r"""
Tweak which monkeypatches docutils to use the following symbols for footnotes:

.. rst-class:: bullet-hidden

* † -- dagger
* ‡ -- double dagger
* § -- section mark
* ¶ -- paragraph mark (pilcrow)
* # -- number sign
* ♠ -- spade suit
* ♥ -- heart suit
* ♦ -- diamond suit
* ♣ -- club suit

With some themes the superscript asterisk becomes very hard to see.

.. versionadded:: 2.7.0
.. extensions:: sphinx_toolbox.tweaks.footnote_symbols

-----

"""  # noqa: D400
#
#  Copyright © 2021 Dominic Davis-Foster <dominic@davis-foster.co.uk>
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.
#

# stdlib
from typing import List

# 3rd party
from docutils.transforms.references import Footnotes
from sphinx.application import Sphinx

# this package
from sphinx_toolbox.utils import SphinxExtMetadata, metadata_add_version

__all__ = ["setup"]

#: The list of symbols
symbols: List[str] = [
		# Entries 1-3 and 5 below are from section 12.51 of
		# The Chicago Manual of Style, 14th edition.
		'†',  # dagger &dagger;
		'‡',  # double dagger &Dagger;
		'§',  # section mark &sect;
		'¶',  # paragraph mark (pilcrow) &para;
		# (parallels ['||'] in CMoS)
		'#',  # number sign
		# The entries below were chosen arbitrarily.
		'♠',  # spade suit &spades;
		'♥',  # heart suit &hearts;
		'♦',  # diamond suit &diams;
		'♣',  # club suit &clubs;
		]


@metadata_add_version
def setup(app: Sphinx) -> SphinxExtMetadata:
	"""
	Setup :mod:`sphinx_toolbox.tweaks.footnote_symbols`.

	:param app: The Sphinx application.
	"""

	Footnotes.symbols = symbols

	return {"parallel_read_safe": True}

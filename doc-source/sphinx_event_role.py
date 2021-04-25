#  Based on Sphinx
#  Copyright (c) 2007-2021 by the Sphinx team.
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#  * Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
#  * Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#  "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#  LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
#  HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
#  SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
#  LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
#  DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
#  THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#  (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
#  OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#

# stdlib
import re

# 3rd party
import sphinx.addnodes
from sphinx.application import Sphinx
from sphinx.util.docfields import GroupedField

event_sig_re = re.compile(r'([a-zA-Z-]+)\s*\((.*)\)')


def parse_event(env, sig, signode):
	m = event_sig_re.match(sig)
	if not m:
		signode += sphinx.addnodes.desc_name(sig, sig)
		return sig
	name, args = m.groups()
	signode += sphinx.addnodes.desc_name(name, name)
	plist = sphinx.addnodes.desc_parameterlist()
	for arg in args.split(','):
		arg = arg.strip()
		plist += sphinx.addnodes.desc_parameter(arg, arg)
	signode += plist
	return name


def setup(app: Sphinx):
	fdesc = GroupedField("parameter", label="Parameters", names=["param"], can_collapse=True)
	app.add_object_type("event", "event", "pair: %s; event", parse_event, doc_field_types=[fdesc])

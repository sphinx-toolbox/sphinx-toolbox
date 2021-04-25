# stdlib
import re

no_flags = re.compile(r"Hello\s+[Ww]orld[.,](Lovely|Horrible) weather, isn't it (.*)\?")
one_flag = re.compile(r"Hello\s+[Ww]orld[.,](Lovely|Horrible) weather, isn't it (.*)\?", flags=re.IGNORECASE)
two_flags = re.compile(
		r"Hello \s+ [Ww]orld [.,] (Lovely|Horrible)\ weather,\ isn't\ it (.*) \?",
		flags=re.ASCII | re.VERBOSE
		)
backticks = re.compile(":py:class:`([A-Za-z_][A-Za-z0-9._]+)`")
leading_whitespace = re.compile("   :py:class:`([A-Za-z_][A-Za-z0-9._]+)`")
trailing_whitespace = re.compile(":py:class:`([A-Za-z_][A-Za-z0-9._]+)`   ")
single_whitespace = re.compile(" :py:class:`([A-Za-z_][A-Za-z0-9._]+)` ")
